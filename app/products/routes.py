from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.products import bp
from app.models import Product, Cart

@bp.route('/')
def products():
    products = Product.query.all()
    return render_template('products/products.html', title='Products', products=products)

@bp.route('/<int:id>')
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('products/product.html', title=product.name, product=product)

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart!')
    return redirect(request.referrer or url_for('products.products'))