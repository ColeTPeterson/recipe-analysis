"""Provides utilities for detecting the application environment."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ENV_DEV = "dev"
ENV_PROD = "prod"
ENV_TEST = "test"

PROJECT_ROOT = Path(__file__).parent.parent


def detect_environment() -> str:
    """Detect the current environment based on environment variables.
    
    Returns:
        str: The detected environment (etc. dev, prod, test)
    """
    env = os.environ.get('APP_ENVIRONMENT')
    if env:
        logger.info(f"Environment explicitly set to: {env}")
        return env.lower()
    
    if os.environ.get('DOCKER_ENVIRONMENT'):
        logger.info("Running in Docker environment")
        return os.environ.get('DOCKER_ENVIRONMENT', ENV_DEV).lower()
    
    logger.info(f"No environment specified, defaulting to: {ENV_DEV}")
    return ENV_DEV


def load_environment_variables(env: Optional[str] = None) -> str:
    """Load environment variables from the appropriate .env file.

    Args:
        env (Optional[str], optional): Optional environment name override. Defaults to None.

    Returns:
        str: The environment that was loaded
    """
    if env is None:
        env = detect_environment()
    
    env_file = f".env.{env}"
    env_path = PROJECT_ROOT / env_file
    
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        default_env_path = PROJECT_ROOT / ".env"
        if default_env_path.exists():
            logger.info(f"Environment file {env_path} not found, loading from {default_env_path}")
            load_dotenv(default_env_path)
        else:
            logger.warning(f"No environment file found at {env_path} or {default_env_path}")
    
    return env


def get_environment_config() -> Dict[str, Any]:
    """Get general environment configuration.
    
    Returns:
        Dict[str, Any]: Environment configuration
    """
    env = load_environment_variables()
    
    return {
        "environment": env,
        "debug": env.lower() != ENV_PROD,
        "project_name": os.environ.get('COMPOSE_PROJECT_NAME', 'recipe_analysis'),
    }


current_env = load_environment_variables()
