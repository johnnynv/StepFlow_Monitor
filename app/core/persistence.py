"""
Persistence Layer for storing executions, steps, and artifacts
"""

import sqlite3
import json
import os
import shutil
import asyncio
import aiosqlite
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..models import Execution, Step, Artifact, ExecutionStatus, StepStatus, ArtifactType

logger = logging.getLogger(__name__)


class PersistenceLayer:
    """Handles data persistence using SQLite and file system"""
    
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.db_path = self.storage_path / "database" / "containerflow.db"
        self.executions_path = self.storage_path / "executions"
        self.artifacts_path = self.storage_path / "artifacts"
        
        # Ensure directories exist
        self.storage_path.mkdir(exist_ok=True)
        self.db_path.parent.mkdir(exist_ok=True)
        self.executions_path.mkdir(exist_ok=True)
        self.artifacts_path.mkdir(exist_ok=True)
        
        self._init_lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize database schema"""
        async with self._init_lock:
            if self._initialized:
                return
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                await self._create_tables(db)
                await db.commit()
            
            self._initialized = True
            logger.info("Persistence layer initialized")
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create database tables"""
        
        # Executions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                command TEXT NOT NULL,
                working_directory TEXT,
                status TEXT NOT NULL,
                exit_code INTEGER,
                error_message TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                environment TEXT,
                user_name TEXT,
                tags TEXT,
                total_steps INTEGER DEFAULT 0,
                completed_steps INTEGER DEFAULT 0,
                current_step_index INTEGER DEFAULT -1,
                metadata TEXT
            )
        """)
        
        # Steps table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                step_index INTEGER NOT NULL,
                status TEXT NOT NULL,
                exit_code INTEGER,
                error_message TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                estimated_duration REAL,
                metadata TEXT,
                FOREIGN KEY (execution_id) REFERENCES executions (id)
            )
        """)
        
        # Artifacts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                step_id TEXT,
                name TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                file_name TEXT,
                file_size INTEGER DEFAULT 0,
                mime_type TEXT,
                artifact_type TEXT,
                created_at TEXT NOT NULL,
                tags TEXT,
                is_public BOOLEAN DEFAULT 1,
                retention_days INTEGER,
                metadata TEXT,
                FOREIGN KEY (execution_id) REFERENCES executions (id),
                FOREIGN KEY (step_id) REFERENCES steps (id)
            )
        """)
        
        # Create indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_executions_status ON executions (status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions (created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_executions_user ON executions (user_name)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_steps_execution_id ON steps (execution_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_steps_status ON steps (status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_execution_id ON artifacts (execution_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_step_id ON artifacts (step_id)")
    
    async def save_execution(self, execution: Execution) -> bool:
        """Save or update execution"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO executions (
                        id, name, command, working_directory, status, exit_code, error_message,
                        created_at, started_at, completed_at, environment, user_name, tags,
                        total_steps, completed_steps, current_step_index, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.id, execution.name, execution.command, execution.working_directory,
                    execution.status.value, execution.exit_code, execution.error_message,
                    execution.created_at.isoformat(),
                    execution.started_at.isoformat() if execution.started_at else None,
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    json.dumps(execution.environment), execution.user, json.dumps(execution.tags),
                    execution.total_steps, execution.completed_steps, execution.current_step_index,
                    json.dumps(execution.metadata)
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save execution {execution.id}: {e}")
            return False
    
    async def save_step(self, step: Step) -> bool:
        """Save or update step"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO steps (
                        id, execution_id, name, description, step_index, status, exit_code, 
                        error_message, created_at, started_at, completed_at, estimated_duration, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step.id, step.execution_id, step.name, step.description, step.index,
                    step.status.value, step.exit_code, step.error_message,
                    step.created_at.isoformat(),
                    step.started_at.isoformat() if step.started_at else None,
                    step.completed_at.isoformat() if step.completed_at else None,
                    step.estimated_duration, json.dumps(step.metadata)
                ))
                await db.commit()
            
            # Save step logs to file
            await self._save_step_logs(step)
            return True
        except Exception as e:
            logger.error(f"Failed to save step {step.id}: {e}")
            return False
    
    async def save_artifact(self, artifact: Artifact) -> bool:
        """Save artifact metadata and copy file to storage"""
        await self._ensure_initialized()
        
        try:
            # Copy artifact file to storage
            storage_file_path = await self._store_artifact_file(artifact)
            if storage_file_path:
                artifact.file_path = str(storage_file_path)
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO artifacts (
                        id, execution_id, step_id, name, description, file_path, file_name,
                        file_size, mime_type, artifact_type, created_at, tags, is_public,
                        retention_days, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    artifact.id, artifact.execution_id, artifact.step_id, artifact.name,
                    artifact.description, artifact.file_path, artifact.file_name,
                    artifact.file_size, artifact.mime_type, artifact.artifact_type.value,
                    artifact.created_at.isoformat(), json.dumps(artifact.tags),
                    artifact.is_public, artifact.retention_days, json.dumps(artifact.metadata)
                ))
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save artifact {artifact.id}: {e}")
            return False
    
    async def _store_artifact_file(self, artifact: Artifact) -> Optional[Path]:
        """Copy artifact file to persistent storage"""
        if not artifact.file_path or not os.path.exists(artifact.file_path):
            return None
        
        try:
            # Create execution-specific directory
            execution_artifacts_dir = self.artifacts_path / artifact.execution_id
            execution_artifacts_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            original_path = Path(artifact.file_path)
            target_path = execution_artifacts_dir / f"{artifact.id}_{original_path.name}"
            
            # Copy file
            await asyncio.get_event_loop().run_in_executor(
                None, shutil.copy2, artifact.file_path, target_path
            )
            
            return target_path
        except Exception as e:
            logger.error(f"Failed to store artifact file: {e}")
            return None
    
    async def _save_step_logs(self, step: Step):
        """Save step logs to file"""
        if not step.logs:
            return
        
        try:
            # Create execution-specific directory
            execution_logs_dir = self.executions_path / step.execution_id
            execution_logs_dir.mkdir(exist_ok=True)
            
            # Save logs
            log_file = execution_logs_dir / f"step_{step.index}_{step.id}.log"
            with open(log_file, 'w', encoding='utf-8') as f:
                for log_entry in step.logs:
                    f.write(f"[{log_entry.timestamp.isoformat()}] {log_entry.content}\n")
        except Exception as e:
            logger.error(f"Failed to save step logs: {e}")
    
    async def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Get execution by ID"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                async with db.execute(
                    "SELECT * FROM executions WHERE id = ?", (execution_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return self._row_to_execution(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id}: {e}")
            return None
    
    async def get_executions(
        self, 
        limit: int = 100, 
        offset: int = 0,
        status: Optional[ExecutionStatus] = None,
        user: Optional[str] = None
    ) -> List[Execution]:
        """Get executions with filtering and pagination"""
        await self._ensure_initialized()
        
        try:
            query = "SELECT * FROM executions WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            if user:
                query += " AND user_name = ?"
                params.append(user)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [self._row_to_execution(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get executions: {e}")
            return []
    
    async def get_steps(self, execution_id: str) -> List[Step]:
        """Get all steps for an execution"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                async with db.execute(
                    "SELECT * FROM steps WHERE execution_id = ? ORDER BY step_index",
                    (execution_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    steps = []
                    for row in rows:
                        step = self._row_to_step(row)
                        # Load logs from file
                        await self._load_step_logs(step)
                        steps.append(step)
                    return steps
        except Exception as e:
            logger.error(f"Failed to get steps for execution {execution_id}: {e}")
            return []
    
    async def get_artifacts(self, execution_id: str) -> List[Artifact]:
        """Get all artifacts for an execution"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                async with db.execute(
                    "SELECT * FROM artifacts WHERE execution_id = ? ORDER BY created_at",
                    (execution_id,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [self._row_to_artifact(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get artifacts for execution {execution_id}: {e}")
            return []
    
    async def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get artifact by ID"""
        await self._ensure_initialized()
        
        try:
            async with aiosqlite.connect(str(self.db_path)) as db:
                async with db.execute(
                    "SELECT * FROM artifacts WHERE id = ?", (artifact_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return self._row_to_artifact(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get artifact {artifact_id}: {e}")
            return None
    
    async def _load_step_logs(self, step: Step):
        """Load step logs from file"""
        try:
            log_file = self.executions_path / step.execution_id / f"step_{step.index}_{step.id}.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and line.startswith('['):
                            # Parse timestamp and content
                            parts = line.split('] ', 1)
                            if len(parts) == 2:
                                timestamp_str = parts[0][1:]  # Remove [
                                content = parts[1]
                                try:
                                    timestamp = datetime.fromisoformat(timestamp_str)
                                    step.add_log(content)
                                    step.logs[-1].timestamp = timestamp
                                except ValueError:
                                    step.add_log(line)
        except Exception as e:
            logger.error(f"Failed to load step logs: {e}")
    
    async def cleanup_expired_data(self, days: int = 30):
        """Clean up old executions and artifacts"""
        await self._ensure_initialized()
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            async with aiosqlite.connect(str(self.db_path)) as db:
                # Get executions to delete
                async with db.execute(
                    "SELECT id FROM executions WHERE created_at < ?", (cutoff_str,)
                ) as cursor:
                    execution_ids = [row[0] for row in await cursor.fetchall()]
                
                # Delete from database
                await db.execute("DELETE FROM artifacts WHERE execution_id IN ({})".format(
                    ','.join('?' * len(execution_ids))
                ), execution_ids)
                await db.execute("DELETE FROM steps WHERE execution_id IN ({})".format(
                    ','.join('?' * len(execution_ids))
                ), execution_ids)
                await db.execute("DELETE FROM executions WHERE id IN ({})".format(
                    ','.join('?' * len(execution_ids))
                ), execution_ids)
                await db.commit()
                
                # Delete files
                for execution_id in execution_ids:
                    execution_dir = self.executions_path / execution_id
                    artifacts_dir = self.artifacts_path / execution_id
                    
                    if execution_dir.exists():
                        shutil.rmtree(execution_dir, ignore_errors=True)
                    if artifacts_dir.exists():
                        shutil.rmtree(artifacts_dir, ignore_errors=True)
            
            logger.info(f"Cleaned up {len(execution_ids)} old executions")
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
    
    def _row_to_execution(self, row) -> Execution:
        """Convert database row to Execution object"""
        return Execution.from_dict({
            'id': row[0],
            'name': row[1],
            'command': row[2],
            'working_directory': row[3],
            'status': row[4],
            'exit_code': row[5],
            'error_message': row[6],
            'created_at': row[7],
            'started_at': row[8],
            'completed_at': row[9],
            'environment': json.loads(row[10]) if row[10] else {},
            'user': row[11],
            'tags': json.loads(row[12]) if row[12] else [],
            'total_steps': row[13],
            'completed_steps': row[14],
            'current_step_index': row[15],
            'metadata': json.loads(row[16]) if row[16] else {}
        })
    
    def _row_to_step(self, row) -> Step:
        """Convert database row to Step object"""
        return Step.from_dict({
            'id': row[0],
            'execution_id': row[1],
            'name': row[2],
            'description': row[3],
            'index': row[4],
            'status': row[5],
            'exit_code': row[6],
            'error_message': row[7],
            'created_at': row[8],
            'started_at': row[9],
            'completed_at': row[10],
            'estimated_duration': row[11],
            'metadata': json.loads(row[12]) if row[12] else {}
        })
    
    def _row_to_artifact(self, row) -> Artifact:
        """Convert database row to Artifact object"""
        return Artifact.from_dict({
            'id': row[0],
            'execution_id': row[1],
            'step_id': row[2],
            'name': row[3],
            'description': row[4],
            'file_path': row[5],
            'file_name': row[6],
            'file_size': row[7],
            'mime_type': row[8],
            'artifact_type': row[9],
            'created_at': row[10],
            'tags': json.loads(row[11]) if row[11] else [],
            'is_public': bool(row[12]),
            'retention_days': row[13],
            'metadata': json.loads(row[14]) if row[14] else {}
        })
    
    async def _ensure_initialized(self):
        """Ensure persistence layer is initialized"""
        if not self._initialized:
            await self.initialize()