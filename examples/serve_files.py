#!/usr/bin/env python3
"""
Independent File Server for Generated Files
Serves the generated files even after the main demo stops
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def start_file_server(port=8080):
    """Start a simple file server for downloads"""
    
    # Check if downloads directory exists
    downloads_dir = Path("web_interface/downloads")
    if not downloads_dir.exists():
        print("❌ Downloads directory not found: web_interface/downloads")
        print("💡 Please run the demo first to generate files")
        sys.exit(1)
    
    # Check if there are files to serve
    files = list(downloads_dir.glob("*"))
    if not files:
        print("❌ No files found in downloads directory")
        print("💡 Please run the demo first to generate files")
        sys.exit(1)
    
    print("=" * 50)
    print("📁 ContainerFlow File Server")
    print("=" * 50)
    print(f"📂 Serving files from: {downloads_dir.absolute()}")
    print(f"🌐 Server URL: http://localhost:{port}")
    print()
    print("📋 Available files:")
    for file in files:
        if file.is_file():
            size = file.stat().st_size
            print(f"  📄 {file.name} ({size} bytes)")
            print(f"     🔗 http://localhost:{port}/{file.name}")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    class FileHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(downloads_dir), **kwargs)
        
        def do_GET(self):
            if self.path == '/':
                # Serve file list
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ContainerFlow Generated Files</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .file-list {{ list-style: none; padding: 0; }}
                        .file-item {{ 
                            background: #f5f5f5; 
                            margin: 10px 0; 
                            padding: 15px; 
                            border-radius: 5px; 
                            border-left: 4px solid #007cba;
                        }}
                        .file-name {{ font-weight: bold; }}
                        .file-size {{ color: #666; font-size: 0.9em; }}
                        a {{ color: #007cba; text-decoration: none; }}
                        a:hover {{ text-decoration: underline; }}
                    </style>
                </head>
                <body>
                    <h1>🐳 ContainerFlow Generated Files</h1>
                    <p>Files generated from the latest workflow execution:</p>
                    <ul class="file-list">
                """
                
                for file in downloads_dir.glob("*"):
                    if file.is_file():
                        size = file.stat().st_size
                        html += f"""
                        <li class="file-item">
                            <div class="file-name">
                                <a href="/{file.name}" download>📄 {file.name}</a>
                            </div>
                            <div class="file-size">{size} bytes</div>
                        </li>
                        """
                
                html += """
                    </ul>
                    <p><small>💡 Right-click links and "Save As" to download files</small></p>
                </body>
                </html>
                """
                
                self.wfile.write(html.encode())
            else:
                # Serve individual files
                super().do_GET()
        
        def log_message(self, format, *args):
            print(f"📥 Downloaded: {args[0].split()[0]}")
    
    # Try to start server
    try:
        with socketserver.TCPServer(("", port), FileHandler) as httpd:
            httpd.serve_forever()
    except OSError:
        print(f"❌ Port {port} is already in use")
        print(f"💡 Try: python3 examples/serve_files.py --port {port + 1}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 File server stopped!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serve generated files")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    args = parser.parse_args()
    
    start_file_server(args.port)