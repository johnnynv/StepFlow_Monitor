"""
Execution model for script execution sessions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Execution:
    """Represents a script execution session"""
    
    # Identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    command: str = ""
    working_directory: str = ""
    
    # Status
    status: ExecutionStatus = ExecutionStatus.PENDING
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution details
    environment: Dict[str, str] = field(default_factory=dict)
    user: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Progress tracking
    total_steps: int = 0
    completed_steps: int = 0
    current_step_index: int = -1
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100
    
    def start(self):
        """Mark execution as started"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, exit_code: int = 0):
        """Mark execution as completed"""
        self.status = ExecutionStatus.COMPLETED if exit_code == 0 else ExecutionStatus.FAILED
        self.exit_code = exit_code
        self.completed_at = datetime.now()
    
    def cancel(self):
        """Mark execution as cancelled"""
        self.status = ExecutionStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def fail(self, error_message: str, exit_code: int = 1):
        """Mark execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.error_message = error_message
        self.exit_code = exit_code
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'working_directory': self.working_directory,
            'status': self.status.value,
            'exit_code': self.exit_code,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'environment': self.environment,
            'user': self.user,
            'tags': self.tags,
            'total_steps': self.total_steps,
            'completed_steps': self.completed_steps,
            'current_step_index': self.current_step_index,
            'duration_seconds': self.duration_seconds,
            'progress_percentage': self.progress_percentage,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Execution':
        """Create from dictionary"""
        execution = cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            command=data.get('command', ''),
            working_directory=data.get('working_directory', ''),
            status=ExecutionStatus(data.get('status', 'pending')),
            exit_code=data.get('exit_code'),
            error_message=data.get('error_message'),
            environment=data.get('environment', {}),
            user=data.get('user'),
            tags=data.get('tags', []),
            total_steps=data.get('total_steps', 0),
            completed_steps=data.get('completed_steps', 0),
            current_step_index=data.get('current_step_index', -1),
            metadata=data.get('metadata', {})
        )
        
        # Parse datetime fields
        if data.get('created_at'):
            execution.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            execution.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            execution.completed_at = datetime.fromisoformat(data['completed_at'])
            
        return execution