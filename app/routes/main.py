from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user
from app import db
from app.models import Product

# Instantiate the main storefront blueprint module
main_bp = Blueprint('main', __name__)

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