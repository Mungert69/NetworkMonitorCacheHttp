"""
Configuration settings for the Flask Cache Server.

This module contains configuration classes for different environments.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Server settings
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Cache settings
    CACHE_DIR = os.environ.get('CACHE_DIR', './cache_files')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 500 * 1024 * 1024))  # 500MB default
    
    # Security settings
    API_KEY = os.environ.get('API_KEY', 'default-api-key-change-in-production')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # File upload settings
    ALLOWED_EXTENSIONS = {'gguf', 'bin', 'txt', 'json', 'dat', 'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Rate limiting (if enabled)
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.environ.get('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))  # seconds

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # In production, require a strong API key
    @classmethod
    def validate_config(cls):
        if cls.API_KEY == 'default-api-key-change-in-production':
            raise ValueError("Please set a strong API_KEY in production!")

class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    API_KEY = 'test-api-key'
    CACHE_DIR = './test_cache_files'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])