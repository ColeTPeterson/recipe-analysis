"""Provides a singleton connection manager for MongoDB database connections;
handles connection creation, management, and resource cleanup through context managers.
"""

import logging
from contextlib import contextmanager
from typing import Generator

import pymongo
from pymongo import MongoClient
from pymongo.database import Database

from config.database import get_mongodb_config

logger = logging.getLogger(__name__)

class MongoDBConnectionManager:
    """Singleton connection manager for MongoDB database.
    Implements the singleton pattern to maintain a single connection per instance.
    
    Attributes:
        db_config (dict): MongoDB configuration parameters
        _client (MongoClient): Active MongoDB client instance
        _instance (MongoDBConnectionManager): Singleton instance reference
    """
    _instance = None

    def __init__(self):
        """Initialize the connection manager with configuration settings."""
        self.db_config = get_mongodb_config()
        self._client = None

    def __new__(cls):
        """Create or return the singleton instance of the connection manager.
        
        Returns:
            MongoDBConnectionManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(MongoDBConnectionManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def connect(self) -> MongoClient:
        """Establish a connection to the MongoDB database. If a connection already exists,
        returns the existing connection. Otherwise, creates a new connection using the configured parameters.
        
        Returns:
            MongoClient: An active MongoDB client connection
            
        Raises:
            pymongo.errors.ConnectionFailure: If the connection attempt fails
        """
        if self._client is None:
            try:
                if self.db_config.get('username') and self.db_config.get('password'):
                    auth_source = self.db_config.get('auth_source', 'admin')
                    uri = f"mongodb://{self.db_config['username']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/?authSource={auth_source}"
                else:
                    uri = f"mongodb://{self.db_config['host']}:{self.db_config['port']}/"

                self._client = pymongo.MongoClient(uri)
                self._client.admin.command('ping')
                logger.info("Connected to MongoDB")
            except pymongo.errors.ConnectionFailure as e:
                logger.error(f"Error connecting to MongoDB: {e}")
                raise
        return self._client
    
    def get_database(self) -> Database:
        """Get a MongoDB database instance using the configured database name.
        
        Returns:
            Database: MongoDB database instance
        """
        client = self.connect()
        db_name = self.db_config.get('database', 'recipe_analysis')
        if not db_name:
            db_name = 'recipe_analysis'
        return client[db_name]
    
    def close(self) -> None:
        """Close the active MongoDB connection if it exists."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")

    @contextmanager
    def get_collection(self, collection_name: str) ->  Generator[pymongo.collection.Collection, None, None]:
        """Context manager for MongoDB collections.
                
        Args:
            collection_name (str): Name of the MongoDB collection to access
            
        Yields:
            pymongo.collection.Collection: The requested MongoDB collection
            
        Example:
            ```
            with connection_manager.get_collection('recipes') as collection:
                results = collection.find({'cuisine': 'Italian'})
            ```
        """
        db = self.get_database()
        collection = db[collection_name]
        try:
            yield collection
        finally:
            pass
