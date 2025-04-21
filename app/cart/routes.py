from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.cart import bp
from app.models import Cart, Product
from app.orders.forms import CheckoutForm

@bp.route('/')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = 0
    for item in cart_items:
        total += item.product.price * item.quantity
    
    return render_template('cart/cart.html', title='Shopping Cart', cart_items=cart_items, total=total)

@bp.route('/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        flash('You cannot remove this item!')
        return redirect(url_for('cart.cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!')
    return redirect(url_for('cart.cart'))

@bp.route('/update/<int:cart_id>/<int:quantity>')
@login_required
def update_cart(cart_id, quantity):
    cart_item = Cart.query.get_or_404(cart_id)
    if cart_item.user_id != current_user.id:
        flash('You cannot update this item!')
        return redirect(url_for('cart.cart'))
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    flash('Cart updated!')
    return redirect(url_for('cart.cart'))