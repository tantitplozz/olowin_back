import os
import logging
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from datetime import datetime

# Configure logger
logger = logging.getLogger("omnicard.db.mongodb")

# MongoDB client
_client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongodb():
    """Connect to MongoDB server"""
    global _client
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/omnicard")
    
    try:
        _client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        # Validate connection
        await _client.admin.command('ping')
        logger.info("Connected to MongoDB")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

async def close_mongodb_connection():
    """Close MongoDB connection"""
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
    return _client[db_name]

async def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Get collection from database"""
    db = await get_database()
    return db[collection_name]

# Generic CRUD operations
async def find_one(collection_name: str, filter_dict: Dict) -> Optional[Dict]:
    """Find a single document in the collection"""
    collection = await get_collection(collection_name)
    result = await collection.find_one(filter_dict)
    return result

async def find_many(
    collection_name: str, 
    filter_dict: Dict = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: List[tuple] = None
) -> List[Dict]:
    """Find multiple documents in the collection"""
    collection = await get_collection(collection_name)
    cursor = collection.find(filter_dict or {})
    
    # Apply sorting if provided
    if sort_by:
        cursor = cursor.sort(sort_by)
        
    # Apply pagination
    cursor = cursor.skip(skip).limit(limit)
    
    # Convert cursor to list
    return await cursor.to_list(length=limit)

async def insert_one(collection_name: str, document: Dict) -> str:
    """Insert a document into the collection"""
    # Add timestamps
    if 'created_at' not in document:
        document['created_at'] = datetime.utcnow()
    if 'updated_at' not in document:
        document['updated_at'] = datetime.utcnow()
    
    collection = await get_collection(collection_name)
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def update_one(collection_name: str, filter_dict: Dict, update_dict: Dict) -> bool:
    """Update a document in the collection"""
    # Add updated_at timestamp
    if '$set' in update_dict:
        update_dict['$set']['updated_at'] = datetime.utcnow()
    else:
        update_dict['$set'] = {'updated_at': datetime.utcnow()}
    
    collection = await get_collection(collection_name)
    result = await collection.update_one(filter_dict, update_dict)
    return result.modified_count > 0

async def delete_one(collection_name: str, filter_dict: Dict) -> bool:
    """Delete a document from the collection"""
    collection = await get_collection(collection_name)
    result = await collection.delete_one(filter_dict)
    return result.deleted_count > 0

# Helper functions
def convert_object_id(document: Dict) -> Dict:
    """Convert ObjectId to string in a document"""
    if document and '_id' in document and isinstance(document['_id'], ObjectId):
        document['_id'] = str(document['_id'])
    return document 