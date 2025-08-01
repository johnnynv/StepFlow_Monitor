"""
Execution Engine for running scripts and capturing output with marker parsing
"""

import asyncio
import subprocess
import threading
import logging
import os
import signal
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from pathlib import Path

from ..models import Execution, Step, Artifact, ExecutionStatus, StepStatus
from .marker_parser import MarkerParser, MarkerType, ParsedMarker

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Engine for executing scripts with real-time marker processing"""
    
    def __init__(self, persistence_layer=None, websocket_server=None):
        self.persistence = persistence_layer
        self.websocket_server = websocket_server
        self.active_executions: Dict[str, Execution] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}
        
    async def execute_script(
        self,
        command: List[str],
        working_directory: str = ".",
        environment: Optional[Dict[str, str]] = None,
        execution_name: str = "",
        user: str = "",
        timeout: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> Execution:
        """Execute a script with marker processing"""
        
        # Create execution record
        execution = Execution(
            name=execution_name or " ".join(command),
            command=" ".join(command),
            working_directory=working_directory,
            environment=environment or {},
            user=user
        )
        
        # Store execution
        self.active_executions[execution.id] = execution
        if self.persistence:
            await self.persistence.save_execution(execution)
        
        try:
            # Start execution
            execution.start()
            await self._notify_execution_update(execution)
            
            # Run the script
            await self._run_script_process(
                execution, command, working_directory, environment, timeout, progress_callback
            )
            
        except Exception as e:
            logger.error(f"Execution {execution.id} failed: {e}")
            execution.fail(str(e))
            await self._notify_execution_update(execution)
        finally:
            # Clean up
            if execution.id in self.active_processes:
                del self.active_processes[execution.id]
            if execution.id in self.active_executions:
                del self.active_executions[execution.id]
            
            # Final save
            if self.persistence:
                await self.persistence.save_execution(execution)
        
        return execution
    
    async def _run_script_process(
        self,
        execution: Execution,
        command: List[str],
        working_directory: str,
        environment: Optional[Dict[str, str]],
        timeout: Optional[int],
        progress_callback: Optional[Callable]
    ):
        """Run the actual script process with real-time output capture"""
        
        # Prepare environment
        env = os.environ.copy()
        if environment:
            env.update(environment)
        
        # Create marker parser
        parser = MarkerParser()
        current_step: Optional[Step] = None
        
        try:
            # Start process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True,
                cwd=working_directory,
                env=env,
                preexec_fn=os.setsid if os.name == 'posix' else None
            )
            
            self.active_processes[execution.id] = process
            
            # Process output line by line
            async for line in self._read_process_output(process):
                if not line.strip():
                    continue
                
                # Parse line for markers
                parsed_marker = parser.parse_line(line)
                
                # Handle different marker types
                if parsed_marker.marker_type == MarkerType.STEP_START:
                    current_step = await self._handle_step_start(
                        execution, parsed_marker, current_step
                    )
                
                elif parsed_marker.marker_type == MarkerType.STEP_COMPLETE:
                    current_step = await self._handle_step_complete(
                        execution, parsed_marker, current_step
                    )
                
                elif parsed_marker.marker_type == MarkerType.STEP_ERROR:
                    current_step = await self._handle_step_error(
                        execution, parsed_marker, current_step
                    )
                
                elif parsed_marker.marker_type == MarkerType.ARTIFACT:
                    await self._handle_artifact(execution, parsed_marker, current_step)
                
                elif parsed_marker.marker_type == MarkerType.META:
                    await self._handle_metadata(execution, parsed_marker, current_step)
                
                elif parsed_marker.marker_type == MarkerType.LOG:
                    await self._handle_log(execution, parsed_marker, current_step)
                
                # Call progress callback
                if progress_callback:
                    await progress_callback(execution, parsed_marker)
            
            # Wait for process completion
            try:
                exit_code = await asyncio.wait_for(
                    self._wait_for_process(process),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Execution {execution.id} timed out")
                await self._terminate_process(process)
                exit_code = -1
                execution.fail("Execution timed out", exit_code)
            
            # Complete any remaining step
            if current_step and not current_step.is_finished:
                current_step.complete(exit_code)
                await self._notify_step_update(execution, current_step)
            
            # Complete execution
            execution.complete(exit_code)
            await self._notify_execution_update(execution)
            
        except Exception as e:
            logger.error(f"Process execution failed: {e}")
            execution.fail(str(e))
            await self._notify_execution_update(execution)
            
            # Clean up process
            if execution.id in self.active_processes:
                process = self.active_processes[execution.id]
                await self._terminate_process(process)
    
    async def _read_process_output(self, process: subprocess.Popen):
        """Async generator for reading process output line by line"""
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                # Read line in thread to avoid blocking
                line = await loop.run_in_executor(None, process.stdout.readline)
                if not line:
                    # Process finished
                    break
                yield line.rstrip('\n\r')
            except Exception as e:
                logger.error(f"Error reading process output: {e}")
                break
    
    async def _wait_for_process(self, process: subprocess.Popen) -> int:
        """Wait for process completion asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process.wait)
    
    async def _terminate_process(self, process: subprocess.Popen):
        """Terminate process gracefully"""
        try:
            if os.name == 'posix':
                # Send SIGTERM to process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                # Wait a bit for graceful shutdown
                await asyncio.sleep(2)
                if process.poll() is None:
                    # Force kill if still running
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            else:
                # Windows
                process.terminate()
                await asyncio.sleep(2)
                if process.poll() is None:
                    process.kill()
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
    
    async def _handle_step_start(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ) -> Step:
        """Handle STEP_START marker"""
        
        # Complete previous step if exists
        if current_step and not current_step.is_finished:
            current_step.complete()
            await self._notify_step_update(execution, current_step)
        
        # Create new step
        step = Step(
            execution_id=execution.id,
            name=marker.step_name,
            index=execution.total_steps,
            estimated_duration=marker.parameters.get('duration')
        )
        
        # Apply metadata from parameters
        if marker.parameters:
            step.metadata.update(marker.parameters)
        
        # Start step
        step.start()
        
        # Update execution
        execution.total_steps += 1
        execution.current_step_index = step.index
        
        # Save and notify
        if self.persistence:
            await self.persistence.save_step(step)
        await self._notify_step_update(execution, step)
        await self._notify_execution_update(execution)
        
        logger.info(f"Started step: {step.name}")
        return step
    
    async def _handle_step_complete(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ) -> Optional[Step]:
        """Handle STEP_COMPLETE marker"""
        
        if current_step and current_step.name == marker.step_name:
            current_step.complete()
            execution.completed_steps += 1
            
            # Save and notify
            if self.persistence:
                await self.persistence.save_step(current_step)
            await self._notify_step_update(execution, current_step)
            await self._notify_execution_update(execution)
            
            logger.info(f"Completed step: {current_step.name}")
            return None  # No current step
        else:
            logger.warning(f"STEP_COMPLETE for unknown step: {marker.step_name}")
            return current_step
    
    async def _handle_step_error(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ) -> Optional[Step]:
        """Handle STEP_ERROR marker"""
        
        if current_step:
            current_step.fail(marker.content)
            
            # Save and notify
            if self.persistence:
                await self.persistence.save_step(current_step)
            await self._notify_step_update(execution, current_step)
            
            logger.error(f"Step failed: {current_step.name} - {marker.content}")
            return None  # No current step
        else:
            logger.warning(f"STEP_ERROR without active step: {marker.content}")
            return current_step
    
    async def _handle_artifact(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ):
        """Handle ARTIFACT marker"""
        
        artifact_info = marker.artifact_info
        if not artifact_info:
            logger.warning(f"Invalid artifact marker: {marker.original_line}")
            return
        
        file_path, description = artifact_info
        
        # Resolve file path
        if not os.path.isabs(file_path):
            file_path = os.path.join(execution.working_directory, file_path)
        
        # Create artifact
        artifact = Artifact(
            execution_id=execution.id,
            step_id=current_step.id if current_step else None,
            name=os.path.basename(file_path),
            description=description,
            file_path=file_path
        )
        
        # Update file info
        artifact.update_file_info()
        
        # Save and notify
        if self.persistence:
            await self.persistence.save_artifact(artifact)
        await self._notify_artifact_update(execution, artifact)
        
        logger.info(f"Registered artifact: {artifact.name}")
    
    async def _handle_metadata(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ):
        """Handle META marker"""
        
        meta_info = marker.meta_key_value
        if not meta_info:
            logger.warning(f"Invalid meta marker: {marker.original_line}")
            return
        
        key, value = meta_info
        
        if current_step:
            current_step.metadata[key] = value
            if self.persistence:
                await self.persistence.save_step(current_step)
            await self._notify_step_update(execution, current_step)
        else:
            execution.metadata[key] = value
            await self._notify_execution_update(execution)
        
        logger.debug(f"Added metadata: {key}={value}")
    
    async def _handle_log(
        self, execution: Execution, marker: ParsedMarker, current_step: Optional[Step]
    ):
        """Handle regular log line"""
        
        if current_step:
            current_step.add_log(marker.content)
            # Notify periodically (not every log line to avoid spam)
            if len(current_step.logs) % 10 == 0:  # Every 10 log lines
                await self._notify_step_update(execution, current_step)
        
    async def _notify_execution_update(self, execution: Execution):
        """Notify about execution updates"""
        if self.websocket_server:
            await self.websocket_server.broadcast_execution_update(execution)
    
    async def _notify_step_update(self, execution: Execution, step: Step):
        """Notify about step updates"""
        if self.websocket_server:
            await self.websocket_server.broadcast_step_update(execution, step)
    
    async def _notify_artifact_update(self, execution: Execution, artifact: Artifact):
        """Notify about artifact updates"""
        if self.websocket_server:
            await self.websocket_server.broadcast_artifact_update(execution, artifact)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.cancel()
            
            # Terminate process
            if execution_id in self.active_processes:
                process = self.active_processes[execution_id]
                await self._terminate_process(process)
            
            await self._notify_execution_update(execution)
            logger.info(f"Cancelled execution: {execution_id}")
            return True
        
        return False
    
    def get_active_executions(self) -> List[Execution]:
        """Get list of currently active executions"""
        return list(self.active_executions.values())
    
    def is_execution_active(self, execution_id: str) -> bool:
        """Check if execution is currently active"""
        return execution_id in self.active_executions