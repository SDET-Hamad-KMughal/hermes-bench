from flask import Blueprint, render_template, redirect, request, flash
from flask_login import current_user, login_required
from app import db
from app.models import Product, CartItem, User, Order
from app.services.logger import log_action  # Instrumented for audit

# Instantiate the checkout blueprint module
checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    """Handle structural cart updates and display the current transactional state matrix."""
    user_id = current_user.id 

    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        product = Product.query.get_or_404(product_id)
        
        existing_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
        
        if existing_item:
            if existing_item.quantity < product.stock:
                existing_item.quantity += 1
                db.session.commit()
                log_action(current_user, f"Incremented quantity for {product.name}") # Logged
                flash(f"Incremented quantity for {product.name}!", "success")
            else:
                flash(f"Cannot add more items. Stock limit reached for {product.name}.", "danger")
        else:
            if product.stock > 0:
                new_item = CartItem(user_id=user_id, product_id=product_id, quantity=1)
                db.session.add(new_item)
                db.session.commit()
                log_action(current_user, f"Added {product.name} to Cart") # Logged
                flash(f"Added {product.name} to your shopping cart!", "success")
            else:
                flash(f"Sorry, {product.name} is currently out of stock.", "danger")
                
        return redirect('/cart')

    items = CartItem.query.filter_by(user_id=user_id).all()
    subtotal = sum(item.product.price * item.quantity for item in items)
    
    return render_template('cart.html', items=items, subtotal=subtotal)

@checkout_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Process order items, deduct user financial credit balances, and commit inventory updates."""
    user = current_user 
    user_id = user.id
    
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        flash("Your cart is empty. Cannot finalize checkout.", "danger")
        return redirect('/')
        
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    
    if user.balance < total_cost:
        flash(f"Transaction Declined: Insufficient funds. Required: ${total_cost}, Available: ${user.balance}", "danger")
        return redirect('/cart')
        
    for item in cart_items:
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
        else:
            flash(f"Transaction Failed: {item.product.name} went out of stock during processing.", "danger")
            return redirect('/cart')
            
    user.balance -= total_cost
    
    new_order = Order(user_id=user_id, total_paid=total_cost)
    db.session.add(new_order)
    
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    log_action(current_user, f"Checkout Successful - Total: ${total_cost}") # Logged
    flash(f"Order finalized successfully! Total paid: ${total_cost}. Your new balance: ${user.balance:.2f}", "success")
    return redirect('/')