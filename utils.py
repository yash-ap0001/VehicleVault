import os
import uuid
from werkzeug.utils import secure_filename
from app import app
from flask import current_app
from sqlalchemy import func
from models import Vehicle, VehicleImage

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
    """Get unique brands from vehicles"""
    return db.session.query(Vehicle.brand).distinct().all()

def get_models_for_brand(brand):
    """Get models for a specific brand"""
    return db.session.query(Vehicle.model).filter(Vehicle.brand == brand).distinct().all()

def get_vehicle_stats():
    """Get vehicle statistics"""
    total_vehicles = Vehicle.query.count()
    active_vehicles = Vehicle.query.filter_by(is_sold=False).count()
    sold_vehicles = Vehicle.query.filter_by(is_sold=True).count()
    
    return {
        'total': total_vehicles,
        'active': active_vehicles,
        'sold': sold_vehicles
    }

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
