from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import httpx
import redis
import pika
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import JSONResponse

app = FastAPI(title="OmniCard API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
def health():
    return JSONResponse(content={"status": "ok"})

@app.get("/")
def root():
    return {"message": "OmniCard Backend is running"}

# Health Check
@app.get("/health")
async def health_check():
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {}
    }
    
    # Check MongoDB
    try:
        client = AsyncIOMotorClient("mongodb://mongodb:27018")
        await client.admin.command('ping')
        status["services"]["mongodb"] = "healthy"
    except Exception as e:
        status["services"]["mongodb"] = f"unhealthy: {str(e)}"

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
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 