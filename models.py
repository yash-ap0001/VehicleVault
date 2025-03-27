from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import enum

@login_manager.user_loader
def load_user(user_id):
    return Dealer.query.get(int(user_id))

class FuelType(enum.Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"
    CNG = "CNG"
    LPG = "LPG"

class VehicleType(enum.Enum):
    CAR = "Car"
    BIKE = "Bike"
    SUV = "SUV"
    TRUCK = "Truck"
    VAN = "Van"

class Dealer(UserMixin, db.Model):
    __tablename__ = 'dealers'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    business_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with vehicles
    vehicles = db.relationship('Vehicle', backref='dealer', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Dealer {self.business_name}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(VehicleType), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    variant = db.Column(db.String(50))
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Float)
    fuel_type = db.Column(db.Enum(FuelType), nullable=False)
    transmission = db.Column(db.String(20))
    color = db.Column(db.String(20))
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    is_sold = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.id'), nullable=False)
    
    # Relationships
    images = db.relationship('VehicleImage', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Vehicle {self.brand} {self.model} ({self.year})>'
    
    @property
    def primary_image(self):
        """Returns the first image or None if no images"""
        return self.images[0] if self.images else None
    
    @property
    def formatted_price(self):
        """Format price in USD based on value"""
        if self.price >= 1000000:  # $1 million+
            return f"${self.price/1000000:.2f} Million"
        else:
            return f"${self.price:,.2f}"

class VehicleImage(db.Model):
    __tablename__ = 'vehicle_images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    
    def __repr__(self):
        return f'<Image {self.filename}>'
