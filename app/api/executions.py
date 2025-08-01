"""
Execution management API endpoints
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models import Execution, Step, ExecutionStatus
from ..core import ExecutionEngine, PersistenceLayer, AuthManager

logger = logging.getLogger(__name__)


class ExecutionsAPI:
    """API endpoints for execution management"""
    
    def __init__(self, execution_engine: ExecutionEngine, persistence: PersistenceLayer, auth: AuthManager):
        self.execution_engine = execution_engine
        self.persistence = persistence
        self.auth = auth
    
    async def create_execution(self, request_data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Create and start a new execution"""
        try:
            # Validate request
            command = request_data.get('command')
            if not command:
                return {"error": "Command is required", "status": 400}
            
            # Parse command
            if isinstance(command, str):
                command = command.split()
            
            # Extract parameters
            working_directory = request_data.get('working_directory', '.')
            environment = request_data.get('environment', {})
            execution_name = request_data.get('name', '')
            timeout = request_data.get('timeout')
            user_name = user.username if user else 'anonymous'
            
            # Start execution asynchronously
            execution = await self.execution_engine.execute_script(
                command=command,
                working_directory=working_directory,
                environment=environment,
                execution_name=execution_name,
                user=user_name,
                timeout=timeout
            )
            
            return {
                "execution": execution.to_dict(),
                "status": 201
            }
            
        except Exception as e:
            logger.error(f"Failed to create execution: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_executions(self, query_params: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Get list of executions with filtering"""
        try:
            # Parse query parameters
            limit = min(int(query_params.get('limit', 50)), 200)  # Max 200
            offset = int(query_params.get('offset', 0))
            status = query_params.get('status')
            user_filter = query_params.get('user')
            
            # Convert status string to enum
            status_filter = None
            if status:
                try:
                    status_filter = ExecutionStatus(status)
                except ValueError:
                    return {"error": f"Invalid status: {status}", "status": 400}
            
            # Get executions
            executions = await self.persistence.get_executions(
                limit=limit,
                offset=offset,
                status=status_filter,
                user=user_filter
            )
            
            return {
                "executions": [exec.to_dict() for exec in executions],
                "limit": limit,
                "offset": offset,
                "count": len(executions),
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_execution(self, execution_id: str, user=None) -> Dict[str, Any]:
        """Get specific execution with steps and artifacts"""
        try:
            execution = await self.persistence.get_execution(execution_id)
            if not execution:
                return {"error": "Execution not found", "status": 404}
            
            # Get steps and artifacts
            steps = await self.persistence.get_steps(execution_id)
            artifacts = await self.persistence.get_artifacts(execution_id)
            
            return {
                "execution": execution.to_dict(),
                "steps": [step.to_dict() for step in steps],
                "artifacts": [artifact.to_dict() for artifact in artifacts],
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return {"error": str(e), "status": 500}
    
    async def cancel_execution(self, execution_id: str, user=None) -> Dict[str, Any]:
        """Cancel a running execution"""
        try:
            success = await self.execution_engine.cancel_execution(execution_id)
            
            if success:
                return {"message": "Execution cancelled", "status": 200}
            else:
                return {"error": "Execution not found or not running", "status": 404}
                
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_execution_logs(self, execution_id: str, step_id: str = None, user=None) -> Dict[str, Any]:
        """Get execution logs, optionally filtered by step"""
        try:
            if step_id:
                # Get specific step logs
                steps = await self.persistence.get_steps(execution_id)
                target_step = next((s for s in steps if s.id == step_id), None)
                
                if not target_step:
                    return {"error": "Step not found", "status": 404}
                
                return {
                    "logs": [log.to_dict() for log in target_step.logs],
                    "step_id": step_id,
                    "status": 200
                }
            else:
                # Get all execution logs
                steps = await self.persistence.get_steps(execution_id)
                all_logs = []
                
                for step in steps:
                    for log in step.logs:
                        log_dict = log.to_dict()
                        log_dict['step_id'] = step.id
                        log_dict['step_name'] = step.name
                        all_logs.append(log_dict)
                
                # Sort by timestamp
                all_logs.sort(key=lambda x: x['timestamp'])
                
                return {
                    "logs": all_logs,
                    "execution_id": execution_id,
                    "status": 200
                }
                
        except Exception as e:
            logger.error(f"Failed to get logs for execution {execution_id}: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_active_executions(self, user=None) -> Dict[str, Any]:
        """Get currently active executions"""
        try:
            active_executions = self.execution_engine.get_active_executions()
            
            return {
                "executions": [exec.to_dict() for exec in active_executions],
                "count": len(active_executions),
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get active executions: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_execution_statistics(self, user=None) -> Dict[str, Any]:
        """Get execution statistics"""
        try:
            # Get recent executions for statistics
            recent_executions = await self.persistence.get_executions(limit=1000)
            
            stats = {
                "total_executions": len(recent_executions),
                "status_breakdown": {},
                "avg_duration": 0,
                "success_rate": 0,
                "active_count": len(self.execution_engine.get_active_executions())
            }
            
            # Calculate statistics
            if recent_executions:
                durations = []
                success_count = 0
                
                for execution in recent_executions:
                    # Status breakdown
                    status = execution.status.value
                    stats["status_breakdown"][status] = stats["status_breakdown"].get(status, 0) + 1
                    
                    # Duration and success rate
                    if execution.duration_seconds:
                        durations.append(execution.duration_seconds)
                    
                    if execution.status == ExecutionStatus.COMPLETED:
                        success_count += 1
                
                # Calculate averages
                if durations:
                    stats["avg_duration"] = sum(durations) / len(durations)
                
                stats["success_rate"] = (success_count / len(recent_executions)) * 100
            
            return {"statistics": stats, "status": 200}
            
        except Exception as e:
            logger.error(f"Failed to get execution statistics: {e}")
            return {"error": str(e), "status": 500}