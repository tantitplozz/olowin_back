import os
import logging
from typing import Dict, List, Any, Optional, TypeVar, Tuple
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from datetime import datetime

# Configure logger
logger = logging.getLogger("omnicard.db.mongodb")

# MongoDB client
_client: Optional[AsyncIOMotorClient] = None

# Type vars for dummy objects
T = TypeVar('T')
DummyResult = TypeVar('DummyResult')

async def connect_to_mongodb() -> None:
    """Connect to MongoDB server"""
    # Using global is necessary here for the singleton pattern
    # pylint: disable=global-statement
    global _client
    
    # Make sure we're using localhost, not mongodb as hostname
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/omnicard")
    
    # Check if the URI contains the wrong hostname
    if "mongodb://" in mongodb_uri and "localhost" not in mongodb_uri and "127.0.0.1" not in mongodb_uri:
        # Replace hostname with localhost
        mongodb_uri = mongodb_uri.replace("mongodb://mongodb", "mongodb://localhost")
    
    logger.info(f"Connecting to MongoDB: {mongodb_uri}")
    
    try:
        _client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        # Validate connection
        await _client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error("Could not connect to MongoDB: %s", e)
        logger.warning("Continuing without MongoDB connection")
        # Don't raise exception to allow the app to start without MongoDB

async def close_mongodb_connection() -> None:
    """Close MongoDB connection"""
    # Using global is necessary here for the singleton pattern
    # pylint: disable=global-statement
    global _client
    
    if _client:
        _client.close()
        _client = None
        logger.info("Closed MongoDB connection")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if _client is None:
        await connect_to_mongodb()
        
    db_name = os.getenv("MONGODB_DATABASE", "omnicard")
    # _client is guaranteed to be non-None here
    if _client is None:
        # If still None after trying to connect, return dummy DB
        logger.warning("Using dummy database - MongoDB connection not available")
        # Create a dummy object with a dict interface for testing
        class DummyDB:
            def __getitem__(self, _: str) -> 'DummyCollection':
                return DummyCollection()
        return DummyDB()  # type: ignore
    
    return _client[db_name]

async def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Get collection from database"""
    db = await get_database()
    return db[collection_name]

# Dummy collection for when MongoDB is unavailable
class DummyCollection:
    """A dummy collection that logs operations but returns empty results"""
    
    async def find_one(self, *args: Any, **kwargs: Any) -> None:
        logger.debug("DummyCollection.find_one called with args=%s, kwargs=%s", args, kwargs)
        return None
        
    async def find(self, *args: Any, **kwargs: Any) -> 'DummyCursor':
        logger.debug("DummyCollection.find called with args=%s, kwargs=%s", args, kwargs)
        class DummyCursor:
            # pylint: disable=unused-argument
            async def to_list(self, length: int, **kwargs: Any) -> List[Any]:
                return []
            
            def skip(self, skip_count: int) -> 'DummyCursor':
                return self
                
            def limit(self, limit_count: int) -> 'DummyCursor':
                return self
                
            def sort(self, sort_list: List[Tuple]) -> 'DummyCursor':
                return self
        return DummyCursor()
        
    async def insert_one(self, document: Dict[str, Any], **kwargs: Any) -> 'DummyInsertOneResult':
        logger.debug("DummyCollection.insert_one called with document=%s, kwargs=%s", document, kwargs)
        class DummyInsertOneResult:
            @property
            def inserted_id(self) -> str:
                return "dummy_id"
        return DummyInsertOneResult()
        
    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any], **kwargs: Any) -> 'DummyUpdateResult':
        logger.debug("DummyCollection.update_one called with filter=%s, update=%s, kwargs=%s", filter_dict, update_dict, kwargs)
        class DummyUpdateResult:
            @property
            def modified_count(self) -> int:
                return 0
        return DummyUpdateResult()
        
    async def delete_one(self, filter_dict: Dict[str, Any], **kwargs: Any) -> 'DummyDeleteResult':
        logger.debug("DummyCollection.delete_one called with filter=%s, kwargs=%s", filter_dict, kwargs)
        class DummyDeleteResult:
            @property
            def deleted_count(self) -> int:
                return 0
        return DummyDeleteResult()

# Generic CRUD operations
async def find_one(collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a single document in the collection"""
    collection = await get_collection(collection_name)
    result = await collection.find_one(filter_dict)
    return result  # type: ignore

async def find_many(
    collection_name: str, 
    filter_dict: Optional[Dict[str, Any]] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """Find multiple documents in the collection"""
    collection = await get_collection(collection_name)
    cursor = collection.find(filter_dict or {})
    
    # Apply sorting if provided
    if sort_by:
        cursor = cursor.sort(sort_by)
        
    # Apply pagination
    cursor = cursor.skip(skip).limit(limit)
    
    # Convert cursor to list
    return await cursor.to_list(length=limit)  # type: ignore

async def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document into the collection"""
    # Add timestamps
    if 'created_at' not in document:
        document['created_at'] = datetime.utcnow()
    if 'updated_at' not in document:
        document['updated_at'] = datetime.utcnow()
    
    collection = await get_collection(collection_name)
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def update_one(collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
    """Update a document in the collection"""
    # Add updated_at timestamp
    if '$set' in update_dict:
        update_dict['$set']['updated_at'] = datetime.utcnow()
    else:
        update_dict['$set'] = {'updated_at': datetime.utcnow()}
    
    collection = await get_collection(collection_name)
    result = await collection.update_one(filter_dict, update_dict)
    return bool(result.modified_count > 0)

async def delete_one(collection_name: str, filter_dict: Dict[str, Any]) -> bool:
    """Delete a document from the collection"""
    collection = await get_collection(collection_name)
    result = await collection.delete_one(filter_dict)
    return bool(result.deleted_count > 0)

# Helper functions
def convert_object_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ObjectId to string in a document"""
    if document and '_id' in document and isinstance(document['_id'], ObjectId):
        document['_id'] = str(document['_id'])
    return document 