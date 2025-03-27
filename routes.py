from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import Dealer, Vehicle, VehicleImage, FuelType, VehicleType
from forms import DealerLoginForm, DealerRegistrationForm, VehicleForm, SearchForm
from utils import save_image, delete_image, get_brands, get_models_for_brand
import os
from sqlalchemy import or_, and_

# Home page route
@app.route('/')
def index():
    featured_vehicles = Vehicle.query.filter_by(is_featured=True, is_sold=False).order_by(Vehicle.created_at.desc()).limit(5).all()
    latest_vehicles = Vehicle.query.filter_by(is_sold=False).order_by(Vehicle.created_at.desc()).limit(10).all()
    
    # Get unique brands for filter
    brands = get_brands()
    
    return render_template('index.html', 
                           featured_vehicles=featured_vehicles,
                           latest_vehicles=latest_vehicles,
                           brands=brands,
                           fuel_types=FuelType,
                           vehicle_types=VehicleType)

# Search results route
@app.route('/search', methods=['GET'])
def search():
    form = SearchForm(request.args)
    
    query = []
    if not form.is_sold.data:
        query.append(Vehicle.is_sold == False)
    
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query.append(or_(
            Vehicle.brand.ilike(search_term),
            Vehicle.model.ilike(search_term),
            Vehicle.variant.ilike(search_term),
            Vehicle.description.ilike(search_term)
        ))
    
    if form.vehicle_type.data:
        query.append(Vehicle.type == form.vehicle_type.data)
    
    if form.brand.data:
        query.append(Vehicle.brand == form.brand.data)
    
    if form.min_price.data:
        query.append(Vehicle.price >= form.min_price.data)
    
    if form.max_price.data:
        query.append(Vehicle.price <= form.max_price.data)
    
    if form.min_year.data:
        query.append(Vehicle.year >= form.min_year.data)
    
    if form.max_year.data:
        query.append(Vehicle.year <= form.max_year.data)
    
    if form.fuel_type.data:
        query.append(Vehicle.fuel_type == form.fuel_type.data)
    
    if query:
        vehicles = Vehicle.query.filter(and_(*query)).order_by(Vehicle.created_at.desc()).all()
    else:
        vehicles = Vehicle.query.filter_by(is_sold=False).order_by(Vehicle.created_at.desc()).all()
    
    # Get unique brands for filter
    brands = get_brands()
    
    return render_template('search_results.html', 
                           vehicles=vehicles, 
                           form=form,
                           brands=brands,
                           fuel_types=FuelType,
                           vehicle_types=VehicleType)

# Vehicle detail route
@app.route('/vehicle/<int:vehicle_id>')
def vehicle_detail(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    # Find similar vehicles (same brand/type, not sold)
    similar_vehicles = Vehicle.query.filter(
        Vehicle.id != vehicle_id,
        Vehicle.brand == vehicle.brand,
        Vehicle.type == vehicle.type,
        Vehicle.is_sold == False
    ).limit(4).all()
    
    return render_template('vehicle_detail.html', vehicle=vehicle, similar_vehicles=similar_vehicles)

# Dealer login route
@app.route('/dealer/login', methods=['GET', 'POST'])
def dealer_login():
    if current_user.is_authenticated:
        return redirect(url_for('dealer_dashboard'))
    
    form = DealerLoginForm()
    
    if form.validate_on_submit():
        dealer = Dealer.query.filter_by(username=form.username.data).first()
        
        if dealer and check_password_hash(dealer.password_hash, form.password.data):
            login_user(dealer, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dealer_dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('dealer_login.html', form=form)

# Dealer logout route
@app.route('/dealer/logout')
@login_required
def dealer_logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Dealer registration route
@app.route('/dealer/register', methods=['GET', 'POST'])
def dealer_register():
    if current_user.is_authenticated:
        return redirect(url_for('dealer_dashboard'))
    
    form = DealerRegistrationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        username_exists = Dealer.query.filter_by(username=form.username.data).first()
        email_exists = Dealer.query.filter_by(email=form.email.data).first()
        
        if username_exists:
            flash('Username already taken. Please choose another.', 'danger')
        elif email_exists:
            flash('Email already registered. Please use another or login.', 'danger')
        else:
            # Create new dealer
            new_dealer = Dealer(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                business_name=form.business_name.data,
                address=form.address.data,
                phone=form.phone.data
            )
            
            db.session.add(new_dealer)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('dealer_login'))
    
    return render_template('dealer_register.html', form=form)

# Dealer dashboard route
@app.route('/dealer/dashboard')
@login_required
def dealer_dashboard():
    # Get dealer's vehicles
    vehicles = Vehicle.query.filter_by(dealer_id=current_user.id).order_by(Vehicle.created_at.desc()).all()
    
    total_vehicles = len(vehicles)
    active_listings = sum(1 for v in vehicles if not v.is_sold)
    sold_vehicles = sum(1 for v in vehicles if v.is_sold)
    
    return render_template('dealer_dashboard.html', 
                           vehicles=vehicles,
                           total_vehicles=total_vehicles,
                           active_listings=active_listings,
                           sold_vehicles=sold_vehicles)

# Add vehicle route
@app.route('/dealer/vehicle/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    form = VehicleForm()
    
    if form.validate_on_submit():
        # Create new vehicle
        new_vehicle = Vehicle(
            type=form.type.data,
            brand=form.brand.data,
            model=form.model.data,
            variant=form.variant.data,
            year=form.year.data,
            mileage=form.mileage.data,
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            color=form.color.data,
            price=form.price.data,
            description=form.description.data,
            features=form.features.data,
            is_featured=form.is_featured.data,
            is_sold=form.is_sold.data,
            dealer_id=current_user.id
        )
        
        db.session.add(new_vehicle)
        db.session.commit()
        
        # Save vehicle images
        if form.images.data:
            for i, image_file in enumerate(form.images.data):
                filename = save_image(image_file)
                if filename:
                    vehicle_image = VehicleImage(
                        filename=filename,
                        is_primary=(i == 0),  # First image is primary
                        vehicle_id=new_vehicle.id
                    )
                    db.session.add(vehicle_image)
            
            db.session.commit()
        
        flash('Vehicle added successfully!', 'success')
        return redirect(url_for('dealer_dashboard'))
    
    return render_template('add_vehicle.html', form=form)

# Edit vehicle route
@app.route('/dealer/vehicle/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if vehicle belongs to the current dealer
    if vehicle.dealer_id != current_user.id:
        flash('You do not have permission to edit this vehicle.', 'danger')
        return redirect(url_for('dealer_dashboard'))
    
    form = VehicleForm(obj=vehicle)
    
    if form.validate_on_submit():
        # Update vehicle details
        vehicle.type = form.type.data
        vehicle.brand = form.brand.data
        vehicle.model = form.model.data
        vehicle.variant = form.variant.data
        vehicle.year = form.year.data
        vehicle.mileage = form.mileage.data
        vehicle.fuel_type = form.fuel_type.data
        vehicle.transmission = form.transmission.data
        vehicle.color = form.color.data
        vehicle.price = form.price.data
        vehicle.description = form.description.data
        vehicle.features = form.features.data
        vehicle.is_featured = form.is_featured.data
        vehicle.is_sold = form.is_sold.data
        
        # Save new images if provided
        if form.images.data and any(img.filename for img in form.images.data):
            for i, image_file in enumerate(form.images.data):
                if image_file.filename:
                    filename = save_image(image_file)
                    if filename:
                        # If no images yet, set as primary
                        is_primary = (i == 0 and not vehicle.images)
                        
                        vehicle_image = VehicleImage(
                            filename=filename,
                            is_primary=is_primary,
                            vehicle_id=vehicle.id
                        )
                        db.session.add(vehicle_image)
        
        db.session.commit()
        flash('Vehicle updated successfully!', 'success')
        return redirect(url_for('dealer_dashboard'))
    
    return render_template('edit_vehicle.html', form=form, vehicle=vehicle)

# Delete vehicle route
@app.route('/dealer/vehicle/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if vehicle belongs to the current dealer
    if vehicle.dealer_id != current_user.id:
        flash('You do not have permission to delete this vehicle.', 'danger')
        return redirect(url_for('dealer_dashboard'))
    
    # Delete all associated images
    for image in vehicle.images:
        delete_image(image.filename)
    
    # Delete the vehicle (cascade will delete images from database)
    db.session.delete(vehicle)
    db.session.commit()
    
    flash('Vehicle deleted successfully!', 'success')
    return redirect(url_for('dealer_dashboard'))

# Delete image route
@app.route('/dealer/vehicle/delete-image/<int:image_id>', methods=['POST'])
@login_required
def delete_image_route(image_id):
    image = VehicleImage.query.get_or_404(image_id)
    vehicle = Vehicle.query.get_or_404(image.vehicle_id)
    
    # Check if vehicle belongs to the current dealer
    if vehicle.dealer_id != current_user.id:
        flash('You do not have permission to delete this image.', 'danger')
        return redirect(url_for('dealer_dashboard'))
    
    was_primary = image.is_primary
    filename = image.filename
    
    # Delete the image file and database record
    delete_image(filename)
    db.session.delete(image)
    
    # If this was the primary image, set another image as primary if available
    if was_primary and vehicle.images:
        next_image = VehicleImage.query.filter_by(vehicle_id=vehicle.id).first()
        if next_image:
            next_image.is_primary = True
    
    db.session.commit()
    
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('edit_vehicle', vehicle_id=vehicle.id))

# API to get models for a brand
@app.route('/api/models/<brand>')
def get_models(brand):
    models = get_models_for_brand(brand)
    return jsonify(models)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Server error"), 500
