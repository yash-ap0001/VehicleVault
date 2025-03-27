from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError
from models import FuelType, VehicleType
import datetime

current_year = datetime.datetime.now().year

class DealerLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DealerRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(max=120)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Register')

class VehicleForm(FlaskForm):
    type = SelectField('Vehicle Type', choices=[(t.name, t.value) for t in VehicleType], validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    variant = StringField('Variant', validators=[Optional(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=current_year+1)])
    mileage = FloatField('Mileage (miles)', validators=[Optional()])
    fuel_type = SelectField('Fuel Type', choices=[(f.name, f.value) for f in FuelType], validators=[DataRequired()])
    transmission = StringField('Transmission', validators=[Optional(), Length(max=20)])
    color = StringField('Color', validators=[Optional(), Length(max=20)])
    price = FloatField('Price ($)', validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[Optional()])
    features = TextAreaField('Features', validators=[Optional()])
    is_featured = BooleanField('Featured Vehicle', default=False)
    is_sold = BooleanField('Sold', default=False)
    images = MultipleFileField('Vehicle Images', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    vehicle_type = SelectField('Type', choices=[('', 'All Types')] + [(t.name, t.value) for t in VehicleType], validators=[Optional()])
    brand = StringField('Brand', validators=[Optional()])
    min_price = FloatField('Min Price ($)', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price ($)', validators=[Optional(), NumberRange(min=0)])
    min_year = IntegerField('Min Year', validators=[Optional(), NumberRange(min=1900, max=current_year+1)])
    max_year = IntegerField('Max Year', validators=[Optional(), NumberRange(min=1900, max=current_year+1)])
    fuel_type = SelectField('Fuel Type', choices=[('', 'All Fuel Types')] + [(f.name, f.value) for f in FuelType], validators=[Optional()])
    submit = SubmitField('Search')
    
    def validate_max_price(self, field):
        if self.min_price.data and field.data and field.data < self.min_price.data:
            raise ValidationError('Maximum price must be greater than minimum price')
    
    def validate_max_year(self, field):
        if self.min_year.data and field.data and field.data < self.min_year.data:
            raise ValidationError('Maximum year must be greater than minimum year')
