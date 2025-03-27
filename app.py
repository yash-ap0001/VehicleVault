import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup database base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with base class
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///vehicles.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "webp"}

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'dealer_login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# Register models and routes within app context
with app.app_context():
    # Import models and routes here to avoid circular imports
    from models import Dealer, Vehicle, VehicleImage  # noqa: F401
    import routes  # noqa: F401
    
    # Create database tables
    db.create_all()
    
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
        app.logger.info("Created test dealer account")
