from fastapi.responses import HTMLResponse
import sys
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request

# Add proper relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary components
try:
    # from metagpt.team import Team # Removed unused import
    from metagpt.roles.di.data_interpreter import DataInterpreter
    # from agent_prompts.promptilus_x import PromptilusXTool # Removed unused import
    print("[DEBUG] MetaGPT DataInterpreter imported successfully.", file=sys.stderr)
except ImportError as e:
    print(f"[ERROR] Failed to import MetaGPT components: {e}", file=sys.stderr)
    print("[ERROR] Please ensure MetaGPT is installed correctly.", file=sys.stderr)
    sys.exit(1)

# --- FastAPI App Setup ---
app = FastAPI()

# Mount static files (CSS, JS, etc.)
# Assuming 'static' and 'templates' are relative to the project root (where main.py will be)
# If server.py is run directly, these paths might need adjustment or main.py should handle CWD.
project_root_for_static = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(project_root_for_static, "static")), name="static")

# Setup templates for serving HTML
templates = Jinja2Templates(directory=os.path.join(project_root_for_static, "templates"))

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"[ERROR] Failed to render template: {e}", file=sys.stderr)
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", status_code=500)

@app.post("/submit_task")
async def submit_task(request: Request):
    """Handle task submission"""
    try:
        data = await request.json()
        task = data.get("task", "")
        
        if not task:
            return {"error": "No task provided"}
        
        # Create a DataInterpreter instance
        di = DataInterpreter()
        
        # Run the task
        # Assuming DataInterpreter's run method is async, if not, it should be called without await
        # and potentially run in a thread pool executor if it's CPU bound.
        result = await di.run(task) # Make sure di.run is an async method
        
        return {"result": str(result)} # Ensure result is serializable
    except Exception as e:
        print(f"[ERROR] Task execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # This allows running the server directly for development/testing.
    # For production, main.py or a proper ASGI server like Gunicorn/Hypercorn should be used.
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, app_dir=os.path.dirname(__file__)) 