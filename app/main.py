"""
Main application entry point
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, Any

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core import (
    MarkerParser, ExecutionEngine, PersistenceLayer, 
    WebSocketServer, WebServer, AuthManager, configure_auth
)
from app.api import ExecutionsAPI, ArtifactsAPI, HealthAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StepFlowApp:
    """Main application class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.running = False
        
        # Initialize components
        self.persistence = PersistenceLayer(
            storage_path=self.config.get('storage_path', 'storage')
        )
        
        self.websocket_server = WebSocketServer(
            host=self.config.get('websocket_host', 'localhost'),
            port=self.config.get('websocket_port', 8765)
        )
        
        self.auth_manager = configure_auth()
        
        self.execution_engine = ExecutionEngine(
            persistence_layer=self.persistence,
            websocket_server=self.websocket_server
        )
        
        # Initialize APIs first
        self.executions_api = ExecutionsAPI(
            self.execution_engine, self.persistence, self.auth_manager
        )
        
        self.web_server = WebServer(
            host=self.config.get('web_host', '0.0.0.0'),
            port=self.config.get('web_port', 8080),
            execution_engine=self.execution_engine,
            executions_api=self.executions_api,
            persistence=self.persistence
        )
        self.artifacts_api = ArtifactsAPI(self.persistence, self.auth_manager)
        self.health_api = HealthAPI(
            self.persistence, self.websocket_server, self.auth_manager
        )
    
    async def start(self):
        """Start the application"""
        logger.info("Starting StepFlow Monitor...")
        
        try:
            # Initialize persistence
            await self.persistence.initialize()
            logger.info("✅ Persistence layer initialized")
            
            # Start WebSocket server
            await self.websocket_server.start()
            logger.info("✅ WebSocket server started")
            
            # Start Web server
            await self.web_server.start()
            logger.info("✅ Web server started")
            
            self.running = True
            logger.info("🚀 StepFlow Monitor is running")
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise
    
    async def stop(self):
        """Stop the application"""
        logger.info("Stopping StepFlow Monitor...")
        
        self.running = False
        
        # Stop WebSocket server
        if self.websocket_server:
            await self.websocket_server.stop()
            logger.info("✅ WebSocket server stopped")
        
        # Stop Web server
        if self.web_server:
            await self.web_server.stop()
            logger.info("✅ Web server stopped")
        
        logger.info("🛑 StepFlow Monitor stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        asyncio.create_task(self.stop())
    
    async def execute_command(self, command: list, **kwargs) -> str:
        """Execute a command and return execution ID"""
        try:
            execution = await self.execution_engine.execute_script(
                command=command,
                **kwargs
            )
            return execution.id
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise


async def main():
    """Main entry point"""
    
    # Configuration
    config = {
        'storage_path': 'storage',
        'websocket_host': '0.0.0.0',
        'websocket_port': 8765,
        'web_host': '0.0.0.0',
        'web_port': 8080,
    }
    
    # Create and start app
    app = StepFlowApp(config)
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())