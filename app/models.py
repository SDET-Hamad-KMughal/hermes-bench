from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """User loader callback required for Flask-Login session management."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Schema representing authenticated users and their financial balance records."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=100.0)  # Starting credit for benchmarking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to track active shopping cart state
    cart_items = db.relationship('CartItem', backref='buyer', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    """Schema representing storefront items, pricing arrays, and inventory counts."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=10)  # Inventory limit constraints
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    """Schema tracking active transactional states before checkout finalization."""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Establish single-point relation join to fetch attached object data easily
    product = db.relationship('Product')