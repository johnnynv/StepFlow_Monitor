"""
Step model for execution steps
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class LogEntry:
    """Individual log entry within a step"""
    timestamp: datetime = field(default_factory=datetime.now)
    content: str = ""
    level: str = "info"  # info, warning, error, debug
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'content': self.content,
            'level': self.level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            content=data.get('content', ''),
            level=data.get('level', 'info')
        )


@dataclass
class Step:
    """Represents a single execution step"""
    
    # Identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = ""
    name: str = ""
    description: str = ""
    index: int = 0
    
    # Status
    status: StepStatus = StepStatus.PENDING
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    
    # Failure Control
    stop_on_error: bool = False
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[float] = None
    
    # Logs
    logs: List[LogEntry] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate step duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None
    
    @property
    def is_finished(self) -> bool:
        """Check if step is finished (completed, failed, or skipped)"""
        return self.status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]
    
    def start(self):
        """Mark step as started"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, exit_code: int = 0):
        """Mark step as completed"""
        self.status = StepStatus.COMPLETED if exit_code == 0 else StepStatus.FAILED
        self.exit_code = exit_code
        self.completed_at = datetime.now()
    
    def fail(self, error_message: str, exit_code: int = 1):
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        self.error_message = error_message
        self.exit_code = exit_code
        self.completed_at = datetime.now()
    
    def skip(self, reason: str = ""):
        """Mark step as skipped"""
        self.status = StepStatus.SKIPPED
        self.error_message = reason
        self.completed_at = datetime.now()
    
    def add_log(self, content: str, level: str = "info") -> LogEntry:
        """Add a log entry to this step"""
        log_entry = LogEntry(content=content, level=level)
        self.logs.append(log_entry)
        return log_entry
    
    def get_logs_text(self) -> str:
        """Get all logs as plain text"""
        return '\n'.join(log.content for log in self.logs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'name': self.name,
            'description': self.description,
            'index': self.index,
            'status': self.status.value,
            'exit_code': self.exit_code,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_duration': self.estimated_duration,
            'duration_seconds': self.duration_seconds,
            'logs': [log.to_dict() for log in self.logs],
            'metadata': self.metadata,
            'is_finished': self.is_finished
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Step':
        """Create from dictionary"""
        step = cls(
            id=data.get('id', str(uuid.uuid4())),
            execution_id=data.get('execution_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            index=data.get('index', 0),
            status=StepStatus(data.get('status', 'pending')),
            exit_code=data.get('exit_code'),
            error_message=data.get('error_message'),
            estimated_duration=data.get('estimated_duration'),
            stop_on_error=data.get('stop_on_error', False),
            metadata=data.get('metadata', {})
        )
        
        # Parse datetime fields
        if data.get('created_at'):
            step.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            step.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            step.completed_at = datetime.fromisoformat(data['completed_at'])
        
        # Parse logs
        if data.get('logs'):
            step.logs = [LogEntry.from_dict(log_data) for log_data in data['logs']]
            
        return step