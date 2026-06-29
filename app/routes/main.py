from flask import Blueprint, render_template
from app.models import Product

# Instantiate the main storefront blueprint module
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the main storefront catalog with live inventory data."""
    products = Product.query.all()
    return render_template('index.html', products=products)