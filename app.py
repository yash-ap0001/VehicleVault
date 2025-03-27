import os
import logging
from urllib.parse import urlparse

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with base class
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLAlchemy
database_url = os.environ.get("DATABASE_URL", "sqlite:///vehicles.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    logger.info(f"Using PostgreSQL database: {database_url}")
else:
    logger.info("Using SQLite database")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "connect_args": {
        "sslmode": "require"  # Enable SSL for Supabase
    }
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
app.config["UPLOAD_FOLDER"] = "/tmp/uploads"  # Use /tmp for serverless
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "webp"}

# Ensure upload directory exists
try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    logger.info(f"Created upload directory: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Error creating upload directory: {str(e)}")

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'dealer_login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# Register models and routes within app context
with app.app_context():
    try:
        # Import models and routes here to avoid circular imports
        from models import Dealer, Vehicle, VehicleImage  # noqa: F401
        import routes  # noqa: F401
        
        # Create database tables
        logger.info("Attempting to create database tables...")
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Add test dealer if none exists
        if not Dealer.query.first():
            from werkzeug.security import generate_password_hash
            test_dealer = Dealer(
                username="testdealer",
                email="test@example.com",
                password_hash=generate_password_hash("password"),
                business_name="Test Dealership",
                address="123 Demo Street",
                phone="555-123-4567"
            )
            db.session.add(test_dealer)
            db.session.commit()
            logger.info("Created test dealer account")
    except Exception as e:
        logger.error(f"Error during app initialization: {str(e)}")
        # Don't raise the exception, just log it
        # This allows the app to start even if database initialization fails
