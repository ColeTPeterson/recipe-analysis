"""Provides database connection managers for both MariaDB and MongoDB;
handles connection creation, management, and resource cleanup.
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from config.database import get_mariadb_config

logger = logging.getLogger(__name__)


class MariaDBConnectionManager:
    """Singleton connection manager for MariaDB database.
    Implements the singleton pattern to maintain a single connection per instance.
    
    Attributes:
        db_config (dict): Database configuration parameters
        _connection (Connection): Active database connection instance
        _instance (MariaDBConnectionManager): Singleton instance reference
    """
    _instance = None

    def __init__(self) -> None:
        """Initialize the connection manager with configuration settings."""
        self.db_config = get_mariadb_config()
        self._connection = None

    def __new__(cls):
        """Create or return the singleton instance of the connection manager.
        
        Returns:
            MariaDBConnectionManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(MariaDBConnectionManager, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def connect(self) -> Connection:
        """Establish a connection to the MariaDB database. If a connection already exists and is open,
        returns the existing connection. Otherwise, creates a new connection using the configured parameters.
        
        Returns:
            Connection: An active database connection
            
        Raises:
            pymysql.Error: If the connection attempt fails
        """
        if self._connection is None or not self._connection.open:
            try:
                self._connection = pymysql.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    user=self.db_config['user'],
                    password=self.db_config['password'],
                    database=self.db_config['database'],
                    cursorclass=DictCursor
                )
                logger.info("Connected to MariaDB")
            except pymysql.Error as e:
                logger.error(f"Error connecting to MariaDB: {e}")
                raise
        return self._connection
    
    def close(self) -> None:
        """Close the active database connection if it exists."""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
            logger.info("Closed connection to MariaDB")

    @contextmanager
    def get_connection(self) -> Generator[Connection, None, None]:
        """Context manager for database connections, yields an active connection.
        
        Yields:
            Connection: Active database connection
            
        Example:
            ```
            with connection_manager.get_connection() as conn:
                # Use the connection directly
                conn.ping()
            ```
        """
        connection = self.connect()
        try:
            yield connection
        finally:
            pass

    @contextmanager
    def get_cursor(self) -> Generator[DictCursor, None, None]:
        """Context manager for database cursors; creates a cursor from an active connection,
        yields it, and handles transactions (commit/rollback) and cursor cleanup.
        
        Yields:
            DictCursor: Database cursor that returns results as dictionaries
            
        Raises:
            Exception: Propagates any exception that occurs during cursor operation
            
        Example:
            ```
            with connection_manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM ingredients")
                results = cursor.fetchall()
            ```
        """
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()


class MongoDBConnectionManager:
    """Singleton connection manager for MongoDB database.
    Implements the singleton pattern to maintain a single connection per instance.
    
    Attributes:
        db_config (dict): MongoDB configuration parameters
        _client (MongoClient): Active MongoDB client instance
        _instance (MongoDBConnectionManager): Singleton instance reference
    """
    _instance = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    _connection_error: Optional[Exception] = None
    
    # MongoDB configuration for different environments
    configs = {
        'dev': {
            'host': os.environ.get('MONGODB_HOST', 'localhost'),
            'port': int(os.environ.get('MONGODB_PORT', '27017')),
            'database': os.environ.get('MONGODB_DATABASE', 'recipe_analysis_dev'),
            'username': os.environ.get('MONGODB_USER'),
            'password': os.environ.get('MONGODB_PASSWORD'),
            'auth_source': os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
        },
        'test': {
            'host': os.environ.get('MONGODB_HOST', 'localhost'),
            'port': int(os.environ.get('MONGODB_PORT', '27017')),
            'database': 'recipe_analysis_test',
            'username': os.environ.get('MONGODB_USER'),
            'password': os.environ.get('MONGODB_PASSWORD'),
            'auth_source': os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
        },
        'prod': {
            'host': os.environ.get('MONGODB_HOST', 'localhost'),
            'port': int(os.environ.get('MONGODB_PORT', '27017')),
            'database': 'recipe_analysis_prod',
            'username': os.environ.get('MONGODB_USER'),
            'password': os.environ.get('MONGODB_PASSWORD'),
            'auth_source': os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
        }
    }
    
    def __new__(cls):
        """Ensure only one instance of the connection manager exists.
        
        Returns:
            MongoDBConnectionManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(MongoDBConnectionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the database connection."""
        self._connect()
    
    def _connect(self) -> bool:
        """Connect to MongoDB.
        
        Returns:
            bool: True if connection was successful
        """
        try:
            # Get environment or default to 'dev'
            env = os.environ.get('APP_ENV', 'dev').lower()
            config = self.configs.get(env, self.configs.get('dev'))
            
            # Connection string with or without authentication
            if config.get('username') and config.get('password'):
                auth_source = config.get('auth_source', 'admin')
                uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={auth_source}"
            else:
                uri = f"mongodb://{config['host']}:{config['port']}"
                
            client_options = {
                'serverSelectionTimeoutMS': 5000
            }
            if config.get('srv'):
                client_options['tlsAllowInvalidCertificates'] = True
                
            self._client = pymongo.MongoClient(uri, **client_options)
            self._db = self._client[config['database']]
            
            # Test the connection
            self._client.admin.command('ping')
            
            logger.info(f"Connected to MongoDB database: {config['database']}")
            self._connection_error = None
            return True
            
        except Exception as e:
            self._connection_error = e
            logger.error(f"Error connecting to MongoDB: {e}")
            return False
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection for performing operations.
            
        Args:
            collection_name (str): Name of the collection to access
            
        Returns:
            Collection: The MongoDB collection object
            
        Raises:
            ConnectionError: If not connected to MongoDB or connection fails
        """
        if self._db is None:
            if self._connection_error is None:
                self._connect()
            
            if self._db is None:
                err_msg = str(self._connection_error) if self._connection_error else "Unknown connection error"
                raise ConnectionError(f"Not connected to MongoDB: {err_msg}")
        
        collection = self._db[collection_name]
        return collection
        
    def ping(self) -> bool:
        """Check if the MongoDB connection is alive.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if not self._client:
            return False
            
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            
    def connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status.
        
        Returns:
            Dict[str, Any]: Connection status information
        """
        status = {
            'connected': self._client is not None and self._db is not None,
            'error': str(self._connection_error) if self._connection_error else None,
            'database': self._db.name if self._db else None,
            'collections': []
        }
        
        if self._db:
            status['collections'] = self._db.list_collection_names()
            
        return status
