#!/usr/bin/env python3
"""
ContainerFlow Visualizer Core - Modular Container Execution Visualization
Professional container execution step visualization tool core module

A lightweight, real-time visualization tool for monitoring container execution workflows.
Separated concerns: WebSocket communication, HTTP serving, and workflow management.
"""

import asyncio
import websockets
import json
import threading
import time
import os
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
from pathlib import Path


class ContainerFlowVisualizer:
    """Main visualizer class for container execution step monitoring"""
    
    def __init__(self, http_port=8080, websocket_port=8765, web_interface_dir="web_interface"):
        self.http_port = http_port
        self.websocket_port = websocket_port
        self.web_interface_directory = Path(web_interface_dir)
        self.connected_clients = set()
        self.current_step_index = 0
        self.total_step_count = 0
        self.execution_steps = []
        self.execution_logs = []
        self.workflow_start_time = None
        
    def add_execution_step(self, step_name, description=""):
        """Add an execution step to the workflow"""
        step_info = {
            "id": len(self.execution_steps),
            "name": step_name,
            "description": description,
            "status": "pending",  # pending, running, completed, failed
            "start_time": None,
            "end_time": None,
            "logs": [],
            "duration_seconds": None
        }
        self.execution_steps.append(step_info)
        self.total_step_count = len(self.execution_steps)
        self._broadcast_status_update()
        
    def start_execution_step(self, step_index):
        """Start executing a specific step"""
        if step_index < len(self.execution_steps):
            self.execution_steps[step_index]["status"] = "running"
            self.execution_steps[step_index]["start_time"] = datetime.now().isoformat()
            self.current_step_index = step_index
            self._broadcast_status_update()
            
    def complete_execution_step(self, step_index, status="completed"):
        """Complete a specific step with given status"""
        if step_index < len(self.execution_steps):
            self.execution_steps[step_index]["status"] = status
            self.execution_steps[step_index]["end_time"] = datetime.now().isoformat()
            if self.execution_steps[step_index]["start_time"]:
                start_time = datetime.fromisoformat(self.execution_steps[step_index]["start_time"])
                end_time = datetime.fromisoformat(self.execution_steps[step_index]["end_time"])
                self.execution_steps[step_index]["duration_seconds"] = (end_time - start_time).total_seconds()
            self._broadcast_status_update()
            
    def add_step_log(self, step_index, message, log_level="info"):
        """Add a log entry for a specific step"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step_index": step_index,
            "level": log_level,
            "message": message
        }
        
        if step_index < len(self.execution_steps):
            self.execution_steps[step_index]["logs"].append(log_entry)
        
        self.execution_logs.append(log_entry)
        self._broadcast_status_update()
        
    def _broadcast_status_update(self):
        """Broadcast status updates to all connected clients"""
        if self.connected_clients:
            status_update = {
                "type": "status_update",
                "data": {
                    "current_step_index": self.current_step_index,
                    "total_step_count": self.total_step_count,
                    "execution_steps": self.execution_steps,
                    "recent_logs": self.execution_logs[-50:],  # Send only recent 50 logs
                    "workflow_start_time": self.workflow_start_time,
                    "update_timestamp": datetime.now().isoformat()
                }
            }
            
            # Schedule async send to all connected clients
            if hasattr(self, '_event_loop') and self._event_loop:
                try:
                    # Schedule the broadcast in the WebSocket event loop
                    asyncio.run_coroutine_threadsafe(
                        self._async_broadcast(status_update), 
                        self._event_loop
                    )
                except Exception as e:
                    print(f"Warning: Failed to broadcast update: {e}")
    
    async def _async_broadcast(self, status_update):
        """Async method to broadcast messages to all clients"""
        disconnected_clients = set()
        message = json.dumps(status_update)
        
        for client in self.connected_clients.copy():  # Use copy to avoid modification during iteration
            try:
                await client.send(message)
            except Exception:
                disconnected_clients.add(client)
        
        # Clean up disconnected clients
        self.connected_clients -= disconnected_clients
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections from clients"""
        self.connected_clients.add(websocket)
        print(f"🔗 Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            # Send current workflow state to new client
            initial_state = {
                "type": "initial_state",
                "data": {
                    "current_step_index": self.current_step_index,
                    "total_step_count": self.total_step_count,
                    "execution_steps": self.execution_steps,
                    "recent_logs": self.execution_logs[-50:],
                    "workflow_start_time": self.workflow_start_time
                }
            }
            await websocket.send(json.dumps(initial_state))
            
            # Keep connection alive and handle client messages
            async for client_message in websocket:
                # Process client messages if needed in the future
                pass
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Safely remove websocket connection
            self.connected_clients.discard(websocket)  # discard won't raise KeyError if not found
            print(f"🔌 Client disconnected. Total clients: {len(self.connected_clients)}")
    
    def start_websocket_server(self):
        """Start the WebSocket server for real-time communication"""
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        self._event_loop = event_loop  # Store event loop for broadcasting
        
        websocket_server = websockets.serve(
            self.handle_websocket_connection, 
            "0.0.0.0", 
            self.websocket_port
        )
        
        print(f"🚀 WebSocket server started on port {self.websocket_port}")
        event_loop.run_until_complete(websocket_server)
        event_loop.run_forever()
    
    def start_http_server(self):
        """Start the HTTP server for serving the web interface"""
        web_dir = self.web_interface_directory
        
        class CustomHTTPHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(web_dir), **kwargs)
        
        with socketserver.TCPServer(("", self.http_port), CustomHTTPHandler) as http_server:
            print(f"🌐 HTTP server started on http://localhost:{self.http_port}")
            print(f"📱 Open http://localhost:{self.http_port}/visualizer.html in your browser")
            http_server.serve_forever()
    
    def start_visualization_service(self):
        """Start the complete visualization service (WebSocket + HTTP)"""
        self.workflow_start_time = datetime.now().isoformat()
        
        # Start WebSocket server in background thread
        websocket_thread = threading.Thread(target=self.start_websocket_server, daemon=True)
        websocket_thread.start()
        
        # Allow WebSocket server to start up
        time.sleep(1)
        
        # Start HTTP server in main thread
        try:
            self.start_http_server()
        except KeyboardInterrupt:
            print("\n🛑 Stopping ContainerFlow Visualizer...")
            sys.exit(0)