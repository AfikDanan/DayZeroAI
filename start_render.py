#!/usr/bin/env python3
"""
Render.com startup script for the preboarding service
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_google_credentials():
    """Setup Google Cloud credentials for Render deployment"""
    from app.config import settings
    
    if settings.GOOGLE_APPLICATION_CREDENTIALS_JSON:
        import json
        import tempfile
        
        try:
            # Parse the JSON credentials
            credentials_dict = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            
            # Create a temporary file for the credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(credentials_dict, f)
                credentials_path = f.name
            
            # Set the environment variable
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            logger.info(f"Google Cloud credentials configured from environment variable")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid Google Cloud credentials JSON: {e}")
            sys.exit(1)
    else:
        logger.info("Using local Google Cloud credentials file")

def setup_directories():
    """Create necessary directories for the application"""
    directories = [
        Path("videos"),
        Path("dev_output"), 
        Path("temp")
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def main():
    """Main startup function"""
    logger.info("🚀 Starting Preboarding Service on Render.com")
    
    # Setup Google Cloud credentials
    setup_google_credentials()
    
    # Create necessary directories
    setup_directories()
    
    # Import and start the FastAPI app
    logger.info("✅ Startup configuration complete")

if __name__ == "__main__":
    main()