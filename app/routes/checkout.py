from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app import db
from app.models import Product, CartItem, User

# Instantiate the checkout blueprint module
checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/cart', methods=['GET', 'POST'])
@login_required  # <-- Restrict cart access to logged-in users only
def cart():
    """Handle structural cart updates and display the current transactional state matrix."""
    user_id = current_user.id  # <-- Use the authenticated user's ID directly

    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        product = Product.query.get_or_404(product_id)
        
        # Check if the product item already exists in this specific user's cart
        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if existing_item:
            # Enforce stock allocation boundaries before increasing quantity
            if existing_item.quantity < product.stock:
                existing_item.quantity += 1
                db.session.commit()
                flash(f"Incremented quantity for {product.name}!", "success")
            else:
                flash(f"Cannot add more items. Stock limit reached for {product.name}.", "danger")
        else:
            # Create a completely brand new transactional cart record row
            if product.stock > 0:
                new_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
                db.session.add(new_item)
                db.session.commit()
                flash(f"Added {product.name} to your shopping cart!", "success")
            else:
                flash(f"Sorry, {product.name} is currently out of stock.", "danger")
                
        return redirect('/cart')

    # GET Request Execution: Fetch and compile all active items inside this user's cart
    items = CartItem.query.filter_by(user_id=user_id).all()
    
    # Calculate order price tallies dynamically
    subtotal = sum(item.product.price * item.quantity for item in items)
    
    return render_template('cart.html', items=items, subtotal=subtotal)

@checkout_bp.route('/checkout', methods=['POST'])
@login_required  # <-- Protect the checkout mutation pipeline
def checkout():
    """Process order items, deduct user financial credit balances, and commit inventory updates."""
    user = current_user  # <-- Bind directly to the securely authenticated user object
    user_id = user.id
    
    # Retrieve all active cart items for this session
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        flash("Your cart is empty. Cannot finalize checkout.", "danger")
        return redirect('/')
        
    # Calculate global deduction totals
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    
    # --- CRITICAL TRANSACTION MUTATION POINT ---
    if user.balance < total_cost:
        flash(f"Transaction Declined: Insufficient funds. Required: ${total_cost}, Available: ${user.balance}", "danger")
        return redirect('/cart')
        
    # Process mutations across all pending catalog items
    for item in cart_items:
        if item.product.stock >= item.quantity:
            # Decrement inventory stock counts
            item.product.stock -= item.quantity
        else:
            flash(f"Transaction Failed: {item.product.name} went out of stock during processing.", "danger")
            return redirect('/cart')
            
    # Deduct transaction cost from the user's ledger balance record
    user.balance -= total_cost
    
    # Clear out processing cart items to mark the order complete
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    flash(f"Order finalized successfully! Total paid: ${total_cost}. Your new balance: ${user.balance:.2f}", "success")
    return redirect('/')