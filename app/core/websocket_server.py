"""
WebSocket Server for real-time communication with frontend
"""

import asyncio
import json
import logging
import websockets
from typing import Set, Dict, Any, Optional
from datetime import datetime

from ..models import Execution, Step, Artifact

logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for real-time communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.running = False
        
    async def start(self):
        """Start the WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            self.running = True
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.running = False
            logger.info("WebSocket server stopped")
    
    async def handle_client(self, websocket, path):
        """Handle new WebSocket client connection"""
        self.connected_clients.add(websocket)
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Send welcome message
            await self.send_to_client(websocket, {
                "type": "connection_established",
                "data": {
                    "client_id": client_id,
                    "server_time": datetime.now().isoformat(),
                    "connected_clients": len(self.connected_clients)
                }
            })
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client {client_id}: {message}")
                except Exception as e:
                    logger.error(f"Error handling message from client {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client {client_id} removed. Total clients: {len(self.connected_clients)}")
    
    async def handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle message from client"""
        message_type = data.get("type")
        
        if message_type == "ping":
            # Respond to ping with pong
            await self.send_to_client(websocket, {
                "type": "pong",
                "data": {"timestamp": datetime.now().isoformat()}
            })
        
        elif message_type == "subscribe_execution":
            # Client wants to subscribe to specific execution updates
            execution_id = data.get("execution_id")
            if execution_id:
                # Store subscription info (could extend this to track subscriptions)
                logger.info(f"Client subscribed to execution {execution_id}")
        
        elif message_type == "get_status":
            # Client requests server status
            await self.send_to_client(websocket, {
                "type": "server_status",
                "data": {
                    "running": self.running,
                    "connected_clients": len(self.connected_clients),
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def send_to_client(self, websocket, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Attempted to send to closed connection")
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.connected_clients:
            return
        
        message_json = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.connected_clients.copy():
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients
        
        if disconnected_clients:
            logger.info(f"Removed {len(disconnected_clients)} disconnected clients")
    
    async def broadcast_execution_update(self, execution: Execution):
        """Broadcast execution status update"""
        await self.broadcast_message({
            "type": "execution_update",
            "data": execution.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_step_update(self, execution: Execution, step: Step):
        """Broadcast step status update"""
        await self.broadcast_message({
            "type": "step_update",
            "data": {
                "execution_id": execution.id,
                "step": step.to_dict(),
                "execution_progress": execution.progress_percentage
            },
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_step_log(self, execution: Execution, step: Step, log_content: str):
        """Broadcast new log entry for a step"""
        await self.broadcast_message({
            "type": "step_log",
            "data": {
                "execution_id": execution.id,
                "step_id": step.id,
                "log_content": log_content,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def broadcast_artifact_update(self, execution: Execution, artifact: Artifact):
        """Broadcast new artifact notification"""
        await self.broadcast_message({
            "type": "artifact_update",
            "data": {
                "execution_id": execution.id,
                "artifact": artifact.to_dict()
            },
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_execution_started(self, execution: Execution):
        """Broadcast execution started notification"""
        await self.broadcast_message({
            "type": "execution_started",
            "data": execution.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_execution_completed(self, execution: Execution):
        """Broadcast execution completed notification"""
        await self.broadcast_message({
            "type": "execution_completed",
            "data": execution.to_dict(),
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_system_notification(self, message: str, level: str = "info"):
        """Broadcast system notification"""
        await self.broadcast_message({
            "type": "system_notification",
            "data": {
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        return len(self.connected_clients)
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running and self.server is not None
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to maintain connections"""
        while self.running:
            await self.broadcast_message({
                "type": "heartbeat",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "connected_clients": len(self.connected_clients)
                }
            })
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds