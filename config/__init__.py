"""Provides utilities for managing application configuration across different
environments (development, production, etc.)
"""
 
from .environment import detect_environment, load_environment_variables, get_environment_config
from .database import get_mariadb_config, get_mongodb_config

__all__ = [
    'detect_environment', 
    'load_environment_variables', 
    'get_environment_config',
    'get_mariadb_config',
    'get_mongodb_config'
]
