"""
Web dashboard server for DevDeck.
Provides a real-time web interface for monitoring and controlling projects.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import os
from pathlib import Path

from core.system_monitor import system_monitor, continuous_monitor
from core.folder_watcher import folder_watcher
from core.log_viewer import log_viewer
from config.config_manager import config_manager

# Initialize FastAPI app
app = FastAPI(title="DevDeck Web Dashboard", version="1.0.0")

# Set up templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Set up static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# WebSocket connections
websocket_connections = set()

# Register callbacks for real-time updates
def on_system_stats(stats):
    """Callback for system statistics updates."""
    # Broadcast to all websocket connections
    async def broadcast():
        if not websocket_connections:
            return
            
        message = json.dumps({
            "type": "system_stats",
            "data": stats
        })
        
        disconnected = set()
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            websocket_connections.discard(websocket)
    
    # Run in event loop
    try:
        # Create a new event loop if needed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast())
    except Exception:
        pass

continuous_monitor.add_callback(on_system_stats)

def on_file_change(path, event_type, file_path):
    """Callback for file change events."""
    async def broadcast():
        if not websocket_connections:
            return
            
        message = json.dumps({
            "type": "file_change",
            "data": {
                "path": path,
                "event_type": event_type,
                "file_path": file_path
            }
        })
        
        disconnected = set()
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            websocket_connections.discard(websocket)
    
    # Run in event loop
    try:
        # Create a new event loop if needed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast())
    except Exception:
        pass

folder_watcher.add_callback(on_file_change)

def on_log_line(line, level):
    """Callback for log line events."""
    async def broadcast():
        if not websocket_connections:
            return
            
        message = json.dumps({
            "type": "log_line",
            "data": {
                "line": line,
                "level": level
            }
        })
        
        disconnected = set()
        for websocket in websocket_connections:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            websocket_connections.discard(websocket)
    
    # Run in event loop
    try:
        # Create a new event loop if needed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(broadcast())
    except Exception:
        pass

log_viewer.add_callback(on_log_line)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.add(websocket)
    
    try:
        # Send initial data
        stats = system_monitor.get_all_stats()
        message = json.dumps({
            "type": "initial_data",
            "data": {
                "projects": [p.to_dict() for p in config_manager.projects],
                "system_stats": stats
            }
        })
        await websocket.send_text(message)
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)  # Ping every 30 seconds
    except Exception:
        pass
    finally:
        websocket_connections.discard(websocket)


@app.get("/api/projects")
async def get_projects():
    """Get all projects."""
    return {"projects": [p.to_dict() for p in config_manager.projects]}


@app.post("/api/projects/{project_name}/start")
async def start_project(project_name: str):
    """Start a project."""
    project = config_manager.get_project(project_name)
    if not project:
        return {"error": "Project not found"}
    
    if project.startup_cmd:
        # In a real implementation, you would actually start the project
        # For now, we'll just simulate it
        return {"message": f"Starting project {project_name}", "command": project.startup_cmd}
    else:
        return {"error": "No startup command configured"}


@app.post("/api/projects/{project_name}/test")
async def test_project(project_name: str):
    """Run tests for a project."""
    project = config_manager.get_project(project_name)
    if not project:
        return {"error": "Project not found"}
    
    if project.test_cmd:
        # In a real implementation, you would actually run the tests
        # For now, we'll just simulate it
        return {"message": f"Running tests for project {project_name}", "command": project.test_cmd}
    else:
        return {"error": "No test command configured"}


@app.post("/api/watch/{path:path}")
async def watch_path_route(path: str):
    """Start watching a path."""
    if folder_watcher.watch_folder(path):
        return {"message": f"Started watching {path}"}
    else:
        return {"error": f"Failed to watch {path}"}


def run_web_server(host="127.0.0.1", port=8000):
    """Run the web server."""
    print(f"Starting DevDeck web server on http://{host}:{port}")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_web_server()
