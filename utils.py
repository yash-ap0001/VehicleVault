import os
import uuid
from werkzeug.utils import secure_filename
from app import app
from flask import current_app

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    """Save an uploaded image to the upload folder with a unique filename"""
    if not file or file.filename == '':
        return None
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent overwriting
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        
        # Save the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return unique_filename
    
    return None

def delete_image(filename):
    """Delete an image file from the upload folder"""
    if not filename:
        return False
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    
    return False

def get_brands():
    """Get a list of all unique vehicle brands from the database"""
    from models import Vehicle
    brands = Vehicle.query.with_entities(Vehicle.brand).distinct().all()
    return [brand[0] for brand in brands]

def get_models_for_brand(brand):
    """Get a list of all unique models for a given brand"""
    from models import Vehicle
    models = Vehicle.query.filter_by(brand=brand).with_entities(Vehicle.model).distinct().all()
    return [model[0] for model in models]

def format_price_for_display(price):
    """Format price in USD for display"""
    if price >= 1000000:  # $1 million+
        return f"${price/1000000:.2f} Million"
    else:
        return f"${price:,.2f}"

def parse_price_input(price_str):
    """Convert a price string in USD to a float value"""
    price_str = price_str.strip()
    
    if "million" in price_str.lower():
        value = float(price_str.lower().replace("million", "").replace("$", "").strip())
        return value * 1000000
    else:
        return float(price_str.replace("$", "").replace(",", "").strip())
