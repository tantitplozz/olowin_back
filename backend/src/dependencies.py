import os
import logging
from typing import Dict, Any, Optional, Union

# Configure logger
logger = logging.getLogger("omnicard.dependencies")

# MongoDB
async def get_mongo_client() -> Optional[Any]:
    """
    Get a MongoDB client instance.
    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/omnicard")
        client = AsyncIOMotorClient(mongodb_uri)
        try:
            # Ping the server to check if the connection is valid
            await client.admin.command('ping')
            return client
        except Exception as e:
            logger.warning("MongoDB connection error: %s", str(e))
            logger.info("Continuing with a dummy MongoDB client")
            # Return a client anyway - operations will be handled by the dummy classes
            return client
    except ImportError:
        logger.warning("motor package not installed, using dummy client")
        return None

async def get_mongodb() -> Optional[Any]:
    """
    Get a MongoDB database instance.
    """
    client = await get_mongo_client()
    db_name = os.getenv("MONGODB_DATABASE", "omnicard")
    return client[db_name] if client else None

# Redis (mock implementation)
class MockRedis:
    """Mock Redis client for development without Redis dependency"""
    
    def __init__(self) -> None:
        self.data: Dict[str, Any] = {}
        self.logger = logging.getLogger("omnicard.mock_redis")
        self.logger.info("Using mock Redis implementation")
    
    def ping(self) -> bool:
        return True
        
    def get(self, key: str) -> Optional[Any]:
        self.logger.debug("MockRedis GET %s", key)
        return self.data.get(key)
        
    def set(self, key: str, value: Any, **kwargs: Any) -> bool:
        self.logger.debug("MockRedis SET %s = %s, kwargs=%s", key, value, kwargs)
        self.data[key] = value
        return True
        
    def delete(self, *keys: str) -> int:
        self.logger.debug("MockRedis DELETE %s", keys)
        count = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                count += 1
        return count
    
    def exists(self, key: str) -> bool:
        self.logger.debug("MockRedis EXISTS %s", key)
        return key in self.data
        
    def expire(self, key: str, seconds: int) -> bool:
        self.logger.debug("MockRedis EXPIRE %s %s", key, seconds)
        # In mock implementation, we don't actually expire keys
        return key in self.data
        
    def incr(self, key: str, amount: int = 1) -> int:
        self.logger.debug("MockRedis INCR %s %s", key, amount)
        if key not in self.data:
            self.data[key] = "0"
        try:
            value = int(self.data[key]) + amount
            self.data[key] = str(value)
            return value
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Value for {key} is not an integer") from exc
    
    def hset(self, name: str, key: str, value: Any) -> int:
        self.logger.debug("MockRedis HSET %s %s %s", name, key, value)
        if name not in self.data:
            self.data[name] = {}
        self.data[name][key] = value
        return 1
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        self.logger.debug("MockRedis HGET %s %s", name, key)
        return self.data.get(name, {}).get(key)
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        self.logger.debug("MockRedis HGETALL %s", name)
        return self.data.get(name, {})

def get_redis_client() -> Union[Any, MockRedis]:
    """
    Get a Redis client instance or mock if Redis is not available.
    """
    try:
        # Try to import Redis
        from redis import Redis
        
        redis_host = os.getenv("REDIS_HOST", "localhost")
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
            logger.info("Connected to Redis")
            return client
        except Exception as e:
            logger.warning("Redis connection error: %s", str(e))
            logger.info("Using mock Redis implementation")
            return MockRedis()
    except ImportError:
        logger.warning("Redis package not installed, using mock implementation")
        return MockRedis()

# Rate limiting dependencies
async def get_rate_limit_config() -> Dict[str, Any]:
    """
    Get rate limiting configuration from environment variables.
    """
    return {
        "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
        "requests": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
        "period": int(os.getenv("RATE_LIMIT_PERIOD", "60")),
    } 