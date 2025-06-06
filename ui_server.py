"""
UI Server for OmniCard-AI system.
Handles frontend serving, WebSocket connections, and API endpoints.
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Standard library imports
from typing import Dict, Any, Optional

# Third-party imports
from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

# Local imports - these will work now that sys.path is updated
from auth.jwt_auth import verify_token  # type: ignore  # noqa: E402
from agents.router_agent import route_prompt  # type: ignore  # noqa: E402
from server.ws import broadcaster  # type: ignore  # noqa: E402

# Constants
PROJECT_ROOT_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = PROJECT_ROOT_DIR / "static"
TEMPLATES_DIR = PROJECT_ROOT_DIR / "templates"
FRONTEND_DIR = PROJECT_ROOT_DIR / "frontend"

templates: Optional[Jinja2Templates] = None

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    print(f"[UIServer] Static directory '{STATIC_DIR}' not found. Skipping static file mount.")

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
else:
    print(f"[UIServer] Templates directory '{TEMPLATES_DIR}' not found. Jinja2Templates not configured.")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend_index(request: Request) -> HTMLResponse:
    frontend_index_path = FRONTEND_DIR / "index.html"
    if frontend_index_path.exists():
        with open(frontend_index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    
    if templates and (TEMPLATES_DIR / "index.html").exists():
        print("[UIServer] frontend/index.html not found, falling back to templates/index.html")
        return templates.TemplateResponse("index.html", {"request": request})  # type: ignore

    return HTMLResponse(content="<html><body><h1>Frontend or Template index.html not found</h1></body></html>", status_code=404)

@app.post("/run_graph")
async def run_graph_api(data: Dict[str, Any], token: str = Depends(verify_token)) -> Dict[str, Any]:
    _ = token  # Acknowledge for auth purposes
    prompt = data.get("prompt")
    if not prompt or not isinstance(prompt, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt must be a non-empty string")

    result = await route_prompt(prompt)
    log_message = f'''Input Prompt:\n{prompt}\n---Agent Response:---\n{result}'''
    await broadcaster.broadcast(log_message)
    return {"result": result}

@app.post("/start_order")
async def start_order_api(data: Dict[str, Any], token: str = Depends(verify_token)) -> Dict[str, Any]:
    _ = token  # Acknowledge for auth purposes
    order_details = data.get("order_details")
    if not order_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order details are required")

    # TODO: Implement the actual logic to start the order workflow
    print(f"[UIServer] Received request to start order with details: {order_details}")
    return {"status": "Order request received", "details": order_details}

@app.websocket("/ws/logs")
async def ws_logs(ws: WebSocket) -> None:
    await broadcaster.connect(ws)
    try:
        while True:
            _ = await ws.receive_text()  # Keep connection alive / consume messages
    except WebSocketDisconnect:
        print(f"[UIServer] WebSocket disconnected from /ws/logs: {ws.client}")
    except Exception as e:
        print(f"[UIServer] Error in /ws/logs WebSocket: {e} for client {ws.client}")
    finally:
        broadcaster.disconnect(ws)
        print(f"[UIServer] WebSocket connection closed and removed for: {ws.client}")

# To run: uvicorn ui_server:app --reload --port 8000