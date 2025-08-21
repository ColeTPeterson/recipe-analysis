"""Provides configuration functions for database connections."""

import os
import logging
from typing import Dict, Any

from config.environment import get_environment_config

logger = logging.getLogger(__name__)

env_config = get_environment_config()
current_env = env_config['environment']
project_name = env_config['project_name']

def get_mariadb_config() -> Dict[str, Any]:
    """Get MariaDB connection configuration from environment variables."""
    host = os.environ.get('MARIADB_HOST', 'localhost')
    port = int(os.environ.get('MARIADB_PORT', 3306))
    user = os.environ.get('MARIADB_USER', 'admin')
    password = os.environ.get('MARIADB_PASSWORD', '')
    
    default_db = f"{project_name}"
    if current_env != "prod":
        default_db = f"{default_db}_{current_env}"
    
    database = os.environ.get('MARIADB_DATABASE', default_db)
    
    logger.info(f"MariaDB Config: host={host}, port={port}, user={user}, database={database} (env: {current_env})")
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

def get_mongodb_config() -> Dict[str, Any]:
    """Get MongoDB connection configuration from environment variables."""
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = int(os.environ.get('MONGODB_PORT', 27017))
    username = os.environ.get('MONGO_INITDB_ROOT_USERNAME', '')
    password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', '')
    
    default_db = f"{project_name}"
    if current_env != "prod":
        default_db = f"{default_db}_{current_env}"
    
    database = os.environ.get('MONGO_INITDB_DATABASE', default_db)
    auth_source = os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
    
    logger.info(f"MongoDB Config: host={host}, port={port}, user={username}, database={database} (env: {current_env})")
    
    return {
        'host': host,
        'port': port,
        'username': username,
        'password': password,
        'database': database,
        'auth_source': auth_source
    }
