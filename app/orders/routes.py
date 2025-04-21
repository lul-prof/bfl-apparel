from flask import current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.orders import bp
from app.orders.forms import CheckoutForm
from app.models import Order, OrderItem, Cart, Product
from datetime import datetime

@bp.route('/history')
@login_required
def order_history():
    """Display the user's order history"""
    orders = Order.query.filter_by(user_id=current_user.id)\
                      .order_by(Order.order_date.desc())\
                      .all()
    return render_template('orders/order_history.html', 
                         title='Order History', 
                         orders=orders)

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart_items = current_user.cart_items.all()
    
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('products.products'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if form.validate_on_submit():
        try:
            # Create order
            order = Order(
                user_id=current_user.id,
                total_amount=total + 200,  # Including shipping
                shipping_address=form.shipping_address.data,
                payment_method=form.payment_method.data,
                payment_status='Pending',
                mpesa_phone=form.phone.data if form.payment_method.data == 'mpesa' else None
            )
            
            db.session.add(order)
            
            # Add order items
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price
                )
                db.session.add(order_item)
                # Update product stock
                item.product.stock -= item.quantity
            
            # Clear cart
            Cart.query.filter_by(user_id=current_user.id).delete()
            
            db.session.commit()
            
            # Redirect to payment processor
            if form.payment_method.data == 'mpesa':
                return redirect(url_for('payments.process_mpesa', order_id=order.id))
            return redirect(url_for('payments.process_paypal', order_id=order.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while processing your order. Please try again.', 'danger')
            current_app.logger.error(f"Order processing error: {str(e)}")
    
    # Pre-fill phone if available
    if current_user.phone:
        form.phone.data = current_user.phone
    
    return render_template('payments/checkout.html',
                         form=form,
                         cart_items=cart_items,
                         total=total)

@bp.route('/<int:order_id>')
@login_required
def order_details(order_id):
    """Display details of a specific order"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure the current user owns this order
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You can only view your own orders', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('orders/order_details.html', 
                         title=f'Order #{order.id}', 
                         order=order)