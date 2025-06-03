import os
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from pika import BlockingConnection, ConnectionParameters
import pika

# MongoDB
async def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get a MongoDB client instance.
    """
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/omnicard")
    client = AsyncIOMotorClient(mongodb_uri)
    try:
        # Ping the server to check if the connection is valid
        await client.admin.command('ping')
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

async def get_mongodb():
    """
    Get a MongoDB database instance.
    """
    client = await get_mongo_client()
    db_name = os.getenv("MONGODB_DATABASE", "omnicard")
    return client[db_name]

# Redis
def get_redis_client() -> Redis:
    """
    Get a Redis client instance.
    """
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    try:
        client = Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True
        )
        # Check connection
        client.ping()
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis connection error: {str(e)}"
        )

# RabbitMQ
def get_rabbitmq_connection() -> BlockingConnection:
    """
    Get a RabbitMQ connection.
    """
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
    rabbitmq_vhost = os.getenv("RABBITMQ_VHOST", "/")
    
    try:
        connection = BlockingConnection(
            ConnectionParameters(
                host=rabbitmq_host,
                port=rabbitmq_port,
                virtual_host=rabbitmq_vhost,
                credentials=pika.PlainCredentials(
                    username=rabbitmq_user,
                    password=rabbitmq_password
                )
            )
        )
        return connection
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RabbitMQ connection error: {str(e)}"
        )

# Rate limiting dependencies
async def get_rate_limit_config():
    """
    Get rate limiting configuration from environment variables.
    """
    return {
        "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
        "requests": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
        "period": int(os.getenv("RATE_LIMIT_PERIOD", "60")),
    } 