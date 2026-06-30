from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, User

# Instantiate the main storefront blueprint module
main_bp = Blueprint('main', __name__)

# Hardcoded Admin email for reliable access in the testbed
ADMIN_EMAIL = "hamad@gmail.com" 

@main_bp.route('/')
def index():
    """Render the main storefront catalog with live inventory data."""
    products = Product.query.all()
    return render_template('index.html', products=products)

@main_bp.route('/topup')
@login_required
def topup():
    """Debug route to reset balance to $100.00 for consistent testing."""
    current_user.balance = 100.0
    db.session.commit()
    flash("Wallet successfully reset to $100.00.", "success")
    return redirect('/')

@main_bp.route('/profile')
@login_required
def profile():
    """Display the current agent's session profile and balance state."""
    return render_template('profile.html')

@main_bp.route('/orders')
@login_required
def orders():
    """Fetch and display the current user's order history."""
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders)

@main_bp.route('/admin')
@login_required
def admin():
    """Read-only view for global state monitoring."""
    # Using email-based authorization for testbed stability
    if current_user.email != ADMIN_EMAIL:
        flash("Admin access restricted.", "danger")
        return redirect('/')
        
    return render_template('admin.html', users=User.query.all(), products=Product.query.all())