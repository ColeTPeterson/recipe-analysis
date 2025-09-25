"""Provides a singleton connection manager for MariaDB database connections;
handles connection creation, management, and resource cleanup through context managers.
"""

import logging
from contextlib import contextmanager
from typing import Generator

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

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
