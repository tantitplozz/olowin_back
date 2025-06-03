from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest
import prometheus_client
import logging
import time
import os
import json
from typing import List
from datetime import datetime
import httpx
import redis
import pika
from motor.motor_asyncio import AsyncIOMotorClient

# Import API routers
from backend.src.api import api_router
from backend.src.db.mongodb import connect_to_mongodb, close_mongodb_connection

app = FastAPI(
    title="OmniCard API",
    description="Multi-Agent System for AI-powered data processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("omnicard")

# Configure middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total", "Total count of API requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "API request latency in seconds", ["method", "endpoint"]
)

# Prometheus middleware
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
            
            # Skip metrics endpoint to avoid recursion
            if request.url.path != "/metrics":
                REQUEST_COUNT.labels(
                    method=request.method, 
                    endpoint=request.url.path,
                    status=status
                ).inc()
                
                REQUEST_LATENCY.labels(
                    method=request.method, 
                    endpoint=request.url.path
                ).observe(time.time() - start_time)
                
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise e

app.add_middleware(PrometheusMiddleware)

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Include API routers
app.include_router(api_router)

# API routes
@app.get("/")
def root():
    return {"message": "OmniCard API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    return JSONResponse(content={"status": "ok"})

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

# WebSocket route
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming data if needed
            await manager.send_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# API endpoints for agents
@app.post("/api/agents/process")
async def process_with_agents(request_data: dict):
    """
    Process data with AI agents.
    
    This endpoint will:
    1. Receive the input data
    2. Process it through the agent workflow
    3. Return the results
    """
    # Placeholder for agent processing logic
    try:
        # Log the incoming request
        logger.info(f"Processing request: {json.dumps(request_data)}")
        
        # Mock response for now
        response = {
            "status": "success",
            "message": "Request processed successfully",
            "data": {
                "input": request_data,
                "output": "Processed result would appear here"
            }
        }
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "agent_update",
            "data": "Processing completed"
        }))
        
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files in production
if os.getenv("ENVIRONMENT") == "production":
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up OmniCard API...")
    # Initialize database connections
    await connect_to_mongodb()
    
    # Health Check
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {}
    }
    
    # Check Redis
    try:
        redis_client = redis.Redis(host='redis', port=6379)
        redis_client.ping()
        status["services"]["redis"] = "healthy"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"

    # Check RabbitMQ
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq')
        )
        connection.close()
        status["services"]["rabbitmq"] = "healthy"
    except Exception as e:
        status["services"]["rabbitmq"] = f"unhealthy: {str(e)}"

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://llm-ollama:11435/api/health")
            if response.status_code == 200:
                status["services"]["ollama"] = "healthy"
            else:
                status["services"]["ollama"] = f"unhealthy: status code {response.status_code}"
    except Exception as e:
        status["services"]["ollama"] = f"unhealthy: {str(e)}"

    # If any service is unhealthy, return 503
    if any("unhealthy" in v for v in status["services"].values()):
        raise HTTPException(status_code=503, detail=status)
    
    logger.info("OmniCard API is healthy")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down OmniCard API...")
    # Close database connections
    await close_mongodb_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 