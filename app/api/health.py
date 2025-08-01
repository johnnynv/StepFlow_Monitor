"""
Health check and system status API endpoints
"""

import logging
import psutil
import asyncio
from typing import Dict, Any
from datetime import datetime

from ..core import PersistenceLayer, WebSocketServer, AuthManager

logger = logging.getLogger(__name__)


class HealthAPI:
    """API endpoints for health checks and system status"""
    
    def __init__(self, persistence: PersistenceLayer, websocket_server: WebSocketServer, auth: AuthManager):
        self.persistence = persistence
        self.websocket_server = websocket_server
        self.auth = auth
        self.start_time = datetime.now()
    
    async def health_check(self) -> Dict[str, Any]:
        """Basic health check"""
        try:
            # Test database connection
            db_healthy = await self._check_database()
            
            # Check WebSocket server
            ws_healthy = self.websocket_server.is_running()
            
            # Overall health
            healthy = db_healthy and ws_healthy
            
            return {
                "status": "healthy" if healthy else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "websocket": "healthy" if ws_healthy else "unhealthy"
                },
                "http_status": 200 if healthy else 503
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "http_status": 503
            }
    
    async def system_status(self) -> Dict[str, Any]:
        """Detailed system status"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # WebSocket info
            ws_clients = self.websocket_server.get_connected_clients_count()
            
            # Database stats
            db_stats = await self._get_database_stats()
            
            return {
                "system": {
                    "uptime_seconds": uptime,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_used_mb": memory.used / 1024 / 1024,
                    "disk_used_gb": disk.used / 1024 / 1024 / 1024
                },
                "services": {
                    "websocket_clients": ws_clients,
                    "websocket_running": self.websocket_server.is_running(),
                    "auth_enabled": self.auth.enabled,
                    "auth_method": self.auth.method.value
                },
                "database": db_stats,
                "timestamp": datetime.now().isoformat(),
                "status": 200
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e), "status": 500}
    
    async def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Try to get a single execution to test database
            await self.persistence.get_executions(limit=1)
            return True
        except Exception:
            return False
    
    async def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            # Get recent executions for counts
            recent_executions = await self.persistence.get_executions(limit=1000)
            
            stats = {
                "total_executions": len(recent_executions),
                "running_executions": len([e for e in recent_executions if e.status.value == "running"]),
                "completed_executions": len([e for e in recent_executions if e.status.value == "completed"]),
                "failed_executions": len([e for e in recent_executions if e.status.value == "failed"])
            }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}