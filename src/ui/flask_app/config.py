"""
Flask Application Configuration

Configuration settings for the Invoice AI Extraction Flask app.
"""

import os
from pathlib import Path

class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'invoice-ai-extraction-secret-key-change-in-production'

    # Upload settings
    UPLOAD_FOLDER = 'data/raw_invoices'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}

    # Processing settings
    MAX_PROCESSING_TIME = 300  # 5 minutes timeout
    CLEANUP_OLD_FILES = True
    CLEANUP_AGE_HOURS = 24  # Delete files older than 24 hours

    # Model settings
    MODEL_CACHE_DIR = 'models/cache'
    GPU_MEMORY_FRACTION = 0.8  # Use 80% of GPU memory

    # Output settings
    RESULTS_DIR = 'data/processed/ai_extractions'
    LOGS_DIR = 'logs'

    # Debug settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SECRET_KEY = 'dev-secret-key-insecure-change-in-production'

    # More permissive in development
    MAX_PROCESSING_TIME = 600  # 10 minutes for debugging
    CLEANUP_AGE_HOURS = 168  # 1 week in development


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Stricter security in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

    # More restrictive processing limits
    MAX_PROCESSING_TIME = 180  # 3 minutes
    CLEANUP_AGE_HOURS = 24  # Clean up more frequently


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'

    # Test directories
    UPLOAD_FOLDER = 'tests/test_data/uploads'
    RESULTS_DIR = 'tests/test_data/results'

    # Disable cleanup in tests
    CLEANUP_OLD_FILES = False


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development').lower()

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }

    return config_map.get(env, DevelopmentConfig)()


def ensure_directories(config):
    """Ensure all required directories exist."""
    directories = [
        config.UPLOAD_FOLDER,
        config.RESULTS_DIR,
        config.LOGS_DIR,
        config.MODEL_CACHE_DIR
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def validate_config(config):
    """Validate configuration settings."""
    errors = []

    # Check required directories
    if not os.path.exists(config.UPLOAD_FOLDER):
        errors.append(f"Upload directory does not exist: {config.UPLOAD_FOLDER}")

    # Check file size limits
    if config.MAX_CONTENT_LENGTH > 50 * 1024 * 1024:  # 50MB
        errors.append("MAX_CONTENT_LENGTH is too high (>50MB)")

    # Check processing time limits
    if config.MAX_PROCESSING_TIME > 600:  # 10 minutes
        errors.append("MAX_PROCESSING_TIME is too high (>10 minutes)")

    return errors


# Global config instance
config = get_config()

# Ensure directories exist
ensure_directories(config)

# Validate configuration
validation_errors = validate_config(config)
if validation_errors:
    print("Configuration validation errors:")
    for error in validation_errors:
        print(f"  - {error}")
    print("Please fix these issues before running the application.")
else:
    print("Configuration validated successfully.")
