"""
Logging configuration for the Invoice AI Extraction System.
"""

import logging
import logging.handlers
from pathlib import Path
from src.config.settings import LOG_LEVEL, LOG_FILE

def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    if LOG_FILE:
        log_path = Path(LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )

    # Add file handler if specified
    if LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)

    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Flask dev server
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)  # SQLAlchemy

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
