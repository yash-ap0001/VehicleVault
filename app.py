import os
import logging
from urllib.parse import urlparse
import time
from sqlalchemy import text

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
database_url = os.environ.get("DATABASE_URL")
logger.info(f"Raw DATABASE_URL: {database_url}")  # Log the raw URL (without password)

if database_url:
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Parse the URL to get connection details (without password)
    parsed_url = urlparse(database_url)
    logger.info(f"Database Host: {parsed_url.hostname}")
    logger.info(f"Database Port: {parsed_url.port}")
    logger.info(f"Database Name: {parsed_url.path[1:]}")
    logger.info(f"Database User: {parsed_url.username}")
    
    # Configure SQLAlchemy with the database URL
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "connect_timeout": 10,  # Add connection timeout
            "sslmode": "require"    # Enable SSL for Supabase
        }
    }
    
    # Test database connection
    try:
        engine = db.create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Successfully connected to PostgreSQL database. Version: {version}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
else:
    logger.warning("No DATABASE_URL found. Using SQLite.")
    database_url = "sqlite:///vehicles.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

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

def init_db():
    """Initialize database with retries"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            db.create_all()
            
            # Test if tables were created
            with db.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables = [row[0] for row in result]
                logger.info(f"Created tables: {tables}")
            
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating database tables (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to create database tables after all retries")
                return False

# Register models and routes within app context
with app.app_context():
    try:
        # Import models and routes here to avoid circular imports
        from models import Dealer, Vehicle, VehicleImage  # noqa: F401
        import routes  # noqa: F401
        
        # Initialize database with retries
        if init_db():
            # Add test dealer if none exists
            try:
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
                logger.error(f"Error creating test dealer: {str(e)}")
        else:
            logger.error("Skipping test dealer creation due to database initialization failure")
    except Exception as e:
        logger.error(f"Error during app initialization: {str(e)}")
        # Don't raise the exception, just log it
        # This allows the app to start even if database initialization fails
