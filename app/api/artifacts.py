"""
Artifact management API endpoints
"""

import os
import mimetypes
import logging
from typing import Dict, Any
from pathlib import Path

from ..models import Artifact
from ..core import PersistenceLayer, AuthManager

logger = logging.getLogger(__name__)


class ArtifactsAPI:
    """API endpoints for artifact management"""
    
    def __init__(self, persistence: PersistenceLayer, auth: AuthManager):
        self.persistence = persistence
        self.auth = auth
    
    async def get_artifact(self, artifact_id: str, user=None) -> Dict[str, Any]:
        """Get artifact metadata"""
        try:
            artifact = await self.persistence.get_artifact(artifact_id)
            if not artifact:
                return {"error": "Artifact not found", "status": 404}
            
            return {
                "artifact": artifact.to_dict(),
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get artifact {artifact_id}: {e}")
            return {"error": str(e), "status": 500}
    
    async def download_artifact(self, artifact_id: str, user=None) -> Dict[str, Any]:
        """Download artifact file"""
        try:
            artifact = await self.persistence.get_artifact(artifact_id)
            if not artifact:
                return {"error": "Artifact not found", "status": 404}
            
            if not artifact.exists:
                return {"error": "Artifact file not found", "status": 404}
            
            # Return file info for download
            return {
                "file_path": artifact.file_path,
                "file_name": artifact.file_name,
                "mime_type": artifact.mime_type,
                "file_size": artifact.file_size,
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to download artifact {artifact_id}: {e}")
            return {"error": str(e), "status": 500}
    
    async def get_execution_artifacts(self, execution_id: str, user=None) -> Dict[str, Any]:
        """Get all artifacts for an execution"""
        try:
            artifacts = await self.persistence.get_artifacts(execution_id)
            
            return {
                "artifacts": [artifact.to_dict() for artifact in artifacts],
                "execution_id": execution_id,
                "count": len(artifacts),
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get artifacts for execution {execution_id}: {e}")
            return {"error": str(e), "status": 500}