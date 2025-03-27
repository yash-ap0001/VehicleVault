import os
import logging
from urllib.parse import urlparse, urlencode, parse_qs
import time
from sqlalchemy import text
from supabase import create_client, Client

from flask import Flask, url_for
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
app = Flask(__name__, 
    static_folder='static',  # Explicitly set static folder
    static_url_path='/static'  # Explicitly set static URL path
)
app.secret_key = os.environ.get("yash_SUPABASE_JWT_SECRET", "dev-secret-key")

# Initialize Supabase client
supabase_url = os.environ.get("yash_SUPABASE_URL")
supabase_key = os.environ.get("yash_SUPABASE_ANON_KEY")
if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Successfully initialized Supabase client")
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {str(e)}")
        supabase = None
else:
    logger.warning("Supabase credentials not found")
    supabase = None

# Configure file uploads
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "webp"}

def get_image_url(filename):
    """Get the public URL for an image from Supabase Storage"""
    try:
        if not filename or not supabase:
            return None
        # Get the public URL for the image
        response = supabase.storage.from_('vehicle-images').get_public_url(filename)
        if isinstance(response, dict):
            return response.get('publicURL')
        return response
    except Exception as e:
        logger.error(f"Error getting image URL: {str(e)}")
        return None

# Add context processor for static files and image URLs
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for, get_image_url=get_image_url)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                   endpoint, filename)
            values['v'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# Configure SQLAlchemy
database_url = os.environ.get("yash_POSTGRES_URL")
logger.info(f"Raw DATABASE_URL: {database_url}")  # Log the raw URL (without password)

if database_url:
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Parse the URL to get connection details (without password)
    parsed_url = urlparse(database_url)
    
    # Clean up query parameters - only keep valid ones
    query_params = parse_qs(parsed_url.query)
    valid_params = {
        'sslmode': query_params.get('sslmode', ['require'])[0]
    }
    
    # Reconstruct the URL with only valid parameters
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    if valid_params:
        clean_url += f"?{urlencode(valid_params)}"
    
    logger.info(f"Database Host: {parsed_url.hostname}")
    logger.info(f"Database Port: {parsed_url.port}")
    logger.info(f"Database Name: {parsed_url.path[1:]}")
    logger.info(f"Database User: {parsed_url.username}")
    
    # Configure SQLAlchemy with the cleaned database URL
    app.config["SQLALCHEMY_DATABASE_URI"] = clean_url
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
        engine = db.create_engine(clean_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Successfully connected to PostgreSQL database. Version: {version}")
            
            # Test if we can query tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"Available tables in database: {tables}")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
else:
    logger.warning("No yash_POSTGRES_URL found. Using SQLite.")
    database_url = "sqlite:///vehicles.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

# Import routes after app is created
from routes import *

# Initialize database
def init_db():
    """Initialize database tables"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to create database tables (attempt {attempt + 1}/{max_retries})...")
            with app.app_context():
                db.create_all()
            logger.info("Database tables created successfully")
            return
        except Exception as e:
            logger.error(f"Error creating database tables (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to create database tables after all retries")
                raise

# Initialize database tables
init_db()

# Create test dealer if none exists
with app.app_context():
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
