"""Contains repository implementations for accessing document-based data
stored in MongoDB, including recipe documents and their associated metadata.
"""

from .connection import MongoDBConnectionManager
from .recipe import RecipeRepository

__all__ = [
    'MongoDBConnectionManager',
    'RecipeRepository'
]
