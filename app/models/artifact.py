"""
Artifact model for generated files and outputs
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import uuid
import os


class ArtifactType(Enum):
    LOG = "log"
    REPORT = "report"
    DATA = "data"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


@dataclass
class Artifact:
    """Represents a generated artifact (file or output)"""
    
    # Identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = ""
    step_id: Optional[str] = None
    name: str = ""
    description: str = ""
    
    # File information
    file_path: str = ""
    file_name: str = ""
    file_size: int = 0
    mime_type: str = ""
    artifact_type: ArtifactType = ArtifactType.OTHER
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    tags: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Access control
    is_public: bool = True
    retention_days: Optional[int] = None
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return os.path.splitext(self.file_name)[1].lower()
    
    @property
    def exists(self) -> bool:
        """Check if artifact file exists"""
        return os.path.exists(self.file_path) if self.file_path else False
    
    @property
    def download_url(self) -> str:
        """Generate download URL"""
        return f"/api/artifacts/{self.id}/download"
    
    @property
    def is_expired(self) -> bool:
        """Check if artifact is expired based on retention policy"""
        if not self.retention_days:
            return False
        expiry_date = self.created_at + timedelta(days=self.retention_days)
        return datetime.now() > expiry_date
    
    def update_file_info(self):
        """Update file size and other info from actual file"""
        if self.exists:
            stat = os.stat(self.file_path)
            self.file_size = stat.st_size
            self.file_name = os.path.basename(self.file_path)
            
            # Determine MIME type based on extension
            mime_types = {
                '.txt': 'text/plain',
                '.log': 'text/plain',
                '.html': 'text/html',
                '.xml': 'text/xml',
                '.json': 'application/json',
                '.csv': 'text/csv',
                '.pdf': 'application/pdf',
                '.zip': 'application/zip',
                '.tar': 'application/x-tar',
                '.gz': 'application/gzip',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif'
            }
            self.mime_type = mime_types.get(self.file_extension, 'application/octet-stream')
    
    def get_human_readable_size(self) -> str:
        """Get human readable file size"""
        if self.file_size == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        size = self.file_size
        i = 0
        
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
            
        return f"{size:.1f} {size_names[i]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'step_id': self.step_id,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_size_human': self.get_human_readable_size(),
            'mime_type': self.mime_type,
            'artifact_type': self.artifact_type.value,
            'file_extension': self.file_extension,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata,
            'is_public': self.is_public,
            'retention_days': self.retention_days,
            'exists': self.exists,
            'download_url': self.download_url,
            'is_expired': self.is_expired
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """Create from dictionary"""
        artifact = cls(
            id=data.get('id', str(uuid.uuid4())),
            execution_id=data.get('execution_id', ''),
            step_id=data.get('step_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            file_path=data.get('file_path', ''),
            file_name=data.get('file_name', ''),
            file_size=data.get('file_size', 0),
            mime_type=data.get('mime_type', ''),
            artifact_type=ArtifactType(data.get('artifact_type', 'other')),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            is_public=data.get('is_public', True),
            retention_days=data.get('retention_days')
        )
        
        # Parse datetime fields
        if data.get('created_at'):
            artifact.created_at = datetime.fromisoformat(data['created_at'])
            
        return artifact