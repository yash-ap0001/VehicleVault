import os
import logging
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# For Vercel deployment
try:
    app = app
    logger.info("Flask app initialized successfully")
except Exception as e:
    logger.error(f"Error initializing Flask app: {str(e)}")
    raise

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
