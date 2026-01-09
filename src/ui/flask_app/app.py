"""
Flask application factory for the Invoice AI Extraction System.

This module creates and configures the Flask app with blueprints, database,
and all necessary components.
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Import blueprints and components
from .api import api_bp
from src.db.session import init_db
from src.config.logging_config import setup_logging

def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'data/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Setup logging
    setup_logging()

    # Initialize database
    init_db()

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register UI routes (basic for now, can be expanded)
    @app.route('/')
    def index():
        return "Invoice AI Extraction System - API available at /api"

    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "invoice-ai-system"}

    return app

# For development server
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
