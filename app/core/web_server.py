"""
HTTP Web Server for serving frontend and API endpoints
"""

import asyncio
import logging
import json
from pathlib import Path
from aiohttp import web
import aiofiles

logger = logging.getLogger(__name__)


class WebServer:
    """HTTP server for web interface and API"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, execution_engine=None, executions_api=None, persistence=None):
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        self.execution_engine = execution_engine
        self.executions_api = executions_api
        self.persistence = persistence
        
        # Path setup
        self.app_path = Path(__file__).parent.parent
        self.static_path = self.app_path / "static"
        self.templates_path = self.app_path / "templates"
    
    def setup_routes(self):
        """Setup all routes"""
        # Static files
        self.app.router.add_static('/static/', self.static_path, name='static')
        
        # API routes
        self.app.router.add_get('/api/health', self.health_check)
        self.app.router.add_get('/api/executions', self.get_executions)
        self.app.router.add_get('/api/executions/active', self.get_active_executions)
        self.app.router.add_get('/api/executions/statistics', self.get_execution_statistics)
        self.app.router.add_get('/api/executions/{execution_id}', self.get_execution)
        self.app.router.add_get('/api/executions/{execution_id}/logs', self.get_execution_logs)
        self.app.router.add_post('/api/executions', self.create_execution)
        
        # Web pages
        self.app.router.add_get('/', self.serve_index)
        self.app.router.add_get('/execution', self.serve_execution)
        self.app.router.add_get('/history', self.serve_history)
        self.app.router.add_get('/artifacts', self.serve_artifacts)
    
    async def serve_index(self, request):
        """Serve the main dashboard page"""
        return await self.serve_template('index.html')
    
    async def serve_execution(self, request):
        """Serve live execution page"""
        return await self.serve_template('execution.html', default_content="""
<!DOCTYPE html>
<html>
<head>
    <title>Live Execution - StepFlow Monitor</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <h1>Live Execution View</h1>
    <p>Real-time execution monitoring will be displayed here.</p>
    <script src="/static/js/websocket.js"></script>
</body>
</html>
        """)
    
    async def serve_history(self, request):
        """Serve execution history page"""
        return await self.serve_template('history.html', default_content="""
<!DOCTYPE html>
<html>
<head>
    <title>Execution History - StepFlow Monitor</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <h1>Execution History</h1>
    <p>Past executions will be listed here.</p>
</body>
</html>
        """)
    
    async def serve_artifacts(self, request):
        """Serve artifacts page"""
        return await self.serve_template('artifacts.html', default_content="""
<!DOCTYPE html>
<html>
<head>
    <title>Artifacts - StepFlow Monitor</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <h1>Artifacts Browser</h1>
    <p>Generated artifacts will be available for download here.</p>
</body>
</html>
        """)
    
    async def serve_template(self, template_name: str, default_content: str = None):
        """Serve HTML template file"""
        template_file = self.templates_path / template_name
        
        try:
            if template_file.exists():
                async with aiofiles.open(template_file, 'r') as f:
                    content = await f.read()
            else:
                content = default_content or f"<h1>Page not found: {template_name}</h1>"
            
            return web.Response(text=content, content_type='text/html')
        except Exception as e:
            logger.error(f"Error serving template {template_name}: {e}")
            return web.Response(text=f"Error loading page: {e}", status=500)
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "StepFlow Monitor",
            "timestamp": "2025-08-01T17:30:00Z"
        })
    
    async def get_executions(self, request):
        """Get list of executions with filtering and pagination"""
        try:
            # Parse query parameters
            limit = int(request.query.get('limit', '50'))
            offset = int(request.query.get('offset', '0'))
            status_filter = request.query.get('status')
            user_filter = request.query.get('user')
            
            # Convert status string to enum if provided
            status_enum = None
            if status_filter:
                from ..models.execution import ExecutionStatus
                try:
                    status_enum = ExecutionStatus(status_filter)
                except ValueError:
                    return web.json_response({
                        "error": f"Invalid status: {status_filter}"
                    }, status=400)
            
            # Use executions API if available
            if self.executions_api:
                query_params = {
                    'limit': limit,
                    'offset': offset,
                    'status': status_filter,
                    'user': user_filter
                }
                result = await self.executions_api.get_executions(query_params)
                return web.json_response(result)
            
            # Fallback: direct persistence access
            elif self.persistence:
                logger.info(f"Fetching {limit} executions from database...")
                executions = await self.persistence.get_executions(
                    limit=limit,
                    offset=offset,
                    status=status_enum,
                    user=user_filter
                )
                logger.info(f"Found {len(executions)} executions in database")
                
                return web.json_response({
                    "executions": [execution.to_dict() for execution in executions],
                    "limit": limit,
                    "offset": offset,
                    "count": len(executions)
                })
            else:
                # Fallback to mock data
                return web.json_response({
                    "executions": [
                        {
                            "id": "exec-123",
                            "status": "completed",
                            "name": "Example Execution (mock)",
                            "start_time": "2025-08-01T17:00:00Z"
                        }
                    ]
                })
        except Exception as e:
            logger.error(f"Error getting executions: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def create_execution(self, request):
        """Create new execution"""
        try:
            data = await request.json()
            command = data.get('command', '')
            name = data.get('name', command)
            
            if not command:
                return web.json_response({
                    "error": "Command is required"
                }, status=400)
            
            # If execution engine is available, use it
            if self.execution_engine:
                try:
                    # Parse command into list
                    command_list = command.split() if isinstance(command, str) else command
                    
                    # Start execution
                    execution = await self.execution_engine.execute_script(
                        command=command_list,
                        execution_name=name,
                        working_directory="."
                    )
                    
                    return web.json_response({
                        "id": execution.id,
                        "status": execution.status.value,
                        "message": "Execution started successfully",
                        "name": execution.name
                    }, status=201)
                except Exception as e:
                    logger.error(f"Failed to start execution: {e}")
                    return web.json_response({
                        "error": f"Failed to start execution: {str(e)}"
                    }, status=500)
            else:
                # Fallback to mock response
                return web.json_response({
                    "id": "exec-" + str(hash(command))[-8:],
                    "status": "started",
                    "message": "Execution started successfully (mock mode)",
                    "warning": "Execution engine not available"
                }, status=201)
                
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=400)
    
    async def get_active_executions(self, request):
        """Get list of active executions"""
        try:
            if self.execution_engine:
                # Get active executions from the engine
                active_executions = []
                for exec_id, execution in self.execution_engine.active_executions.items():
                    if execution.status.value in ["running", "pending"]:
                        active_executions.append({
                            "id": execution.id,
                            "status": execution.status.value,
                            "name": execution.name,
                            "start_time": execution.started_at.isoformat() if execution.started_at else None,
                            "command": execution.command,
                            "created_at": execution.created_at.isoformat() if execution.created_at else None
                        })
                return web.json_response({"active_executions": active_executions})
            else:
                # Fallback to mock data
                return web.json_response({"active_executions": []})
        except Exception as e:
            logger.error(f"Error getting active executions: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_execution_statistics(self, request):
        """Get execution statistics"""
        try:
            if hasattr(self, 'executions_api') and self.executions_api:
                # Use the proper executions API for statistics
                result = await self.executions_api.get_execution_statistics()
                if result.get("status") == 200:
                    stats = result.get("statistics", {})
                    # Format the response to match frontend expectations
                    return web.json_response({
                        "total_executions": stats.get("total_executions", 0),
                        "active_now": stats.get("active_count", 0),
                        "success_rate": f"{stats.get('success_rate', 0):.1f}%",
                        "avg_duration": f"{stats.get('avg_duration', 0):.1f}s" if stats.get('avg_duration', 0) > 0 else "-"
                    })
                else:
                    return web.json_response({"error": result.get("error", "Unknown error")}, status=result.get("status", 500))
            else:
                # Fallback - manually calculate from persistence layer
                if hasattr(self, 'persistence') and self.persistence:
                    executions = await self.persistence.get_executions(limit=1000)
                    total_executions = len(executions)
                    
                    if total_executions > 0:
                        completed = len([ex for ex in executions if ex.status.value == "completed"])
                        failed = len([ex for ex in executions if ex.status.value == "failed"])
                        success_rate = (completed / total_executions) * 100
                        
                        # Calculate average duration for completed executions only (exclude running ones with inflated duration)
                        durations = [ex.duration_seconds for ex in executions if ex.duration_seconds and ex.status.value == "completed" and ex.completed_at is not None]
                        avg_duration = sum(durations) / len(durations) if durations else 0
                    else:
                        success_rate = 0
                        avg_duration = 0
                    
                    # Get active executions count
                    active_now = len(self.execution_engine.active_executions) if self.execution_engine else 0
                    
                    return web.json_response({
                        "total_executions": total_executions,
                        "active_now": active_now,
                        "success_rate": f"{success_rate:.1f}%",
                        "avg_duration": f"{avg_duration:.1f}s" if avg_duration > 0 else "-"
                    })
                else:
                    # Final fallback
                    return web.json_response({
                        "total_executions": 0,
                        "active_now": 0,
                        "success_rate": "0.0%",
                        "avg_duration": "-"
                    })
        except Exception as e:
            logger.error(f"Error getting execution statistics: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_execution(self, request):
        """Get details of a specific execution with steps and artifacts"""
        try:
            execution_id = request.match_info['execution_id']
            
            # Use executions API if available
            if self.executions_api:
                result = await self.executions_api.get_execution(execution_id)
                return web.json_response(result)
            
            # Fallback: direct persistence access
            elif self.persistence:
                try:
                    execution = await self.persistence.get_execution(execution_id)
                    if not execution:
                        return web.json_response({"error": "Execution not found"}, status=404)
                    
                    # Get steps and artifacts
                    steps = await self.persistence.get_steps(execution_id)
                    artifacts = await self.persistence.get_artifacts(execution_id)
                    
                    return web.json_response({
                        "execution": execution.to_dict(),
                        "steps": [step.to_dict() for step in steps],
                        "artifacts": [artifact.to_dict() for artifact in artifacts]
                    })
                except Exception as e:
                    logger.error(f"Failed to get execution from database: {e}")
                    return web.json_response({"error": str(e)}, status=500)
            else:
                # Fallback to mock data
                return web.json_response({
                    "execution": {
                        "id": execution_id,
                        "name": "Mock Execution",
                        "command": "echo 'mock'",
                        "status": "completed",
                        "start_time": "2025-08-01T18:00:00Z",
                        "end_time": "2025-08-01T18:00:05Z"
                    },
                    "steps": [],
                    "artifacts": []
                })
                
        except Exception as e:
            logger.error(f"Error getting execution {execution_id}: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_execution_logs(self, request):
        """Get logs for a specific execution"""
        try:
            execution_id = request.match_info['execution_id']
            
            if self.execution_engine:
                # Look for the execution
                execution = self.execution_engine.active_executions.get(execution_id)
                if execution:
                    # For now, return a simple log structure
                    # In a real implementation, logs would be stored and retrieved
                    logs = [
                        {
                            "timestamp": "2025-08-01T18:00:00Z",
                            "level": "INFO",
                            "message": f"Execution {execution.name} started"
                        },
                        {
                            "timestamp": "2025-08-01T18:00:01Z",
                            "level": "INFO", 
                            "message": f"Command: {execution.command}"
                        },
                        {
                            "timestamp": "2025-08-01T18:00:02Z",
                            "level": "INFO",
                            "message": f"Status: {execution.status.value}"
                        }
                    ]
                    return web.json_response({"logs": logs})
                else:
                    return web.json_response({"error": "Execution not found"}, status=404)
            else:
                # Fallback to mock logs
                return web.json_response({
                    "logs": [
                        {"timestamp": "2025-08-01T18:00:00Z", "level": "INFO", "message": "Mock log entry"}
                    ]
                })
                
        except Exception as e:
            logger.error(f"Error getting execution logs for {execution_id}: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def start(self):
        """Start the web server"""
        try:
            self.app = web.Application()
            self.setup_routes()
            
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"✅ Web server started on http://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            raise
    
    async def stop(self):
        """Stop the web server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("✅ Web server stopped")