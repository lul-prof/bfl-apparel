from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.admin import bp
from app.admin.forms import ProductForm
from app.models import Product
from .decorator import admin_required
from app.models import Product, User, Order
from app.models import Order, OrderItem  
from app.models import User 

UPLOAD_FOLDER = 'app/static/images/products/'

@bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('admin/users.html', 
                         pagination=pagination,
                         users=pagination.items)

@bp.route('/user/make-admin/<int:user_id>', methods=['POST'])
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.username} is now an admin', 'success')
    return redirect(url_for('admin.users'))

@bp.route('/user/remove-admin/<int:user_id>', methods=['POST'])
@login_required
def remove_admin(user_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot remove your own admin status', 'danger')
    else:
        user.is_admin = False
        db.session.commit()
        flash(f'{user.username} is no longer an admin', 'success')
    return redirect(url_for('admin.users'))




@bp.route('/orders')
@login_required
def orders():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    # Build base query
    query = Order.query.order_by(Order.order_date.desc())
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter(Order.status == status_filter)
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/orders.html',
                         pagination=pagination,
                         orders=pagination.items,
                         status_filter=status_filter)

@bp.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_details.html', order=order)

@bp.route('/order/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}', 'success')
    
    return redirect(url_for('admin.order_details', order_id=order.id))

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    # Get counts for the dashboard
    product_count = Product.query.count()
    user_count = User.query.count()
    order_count = Order.query.count()

    return render_template('admin/dashboard.html', 
                            product_count=product_count,
                            user_count=user_count,
                            order_count=order_count)

@bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))

    form = ProductForm()
    
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        product = Product(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            stock=form.stock.data,
            image=filename
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))  # fixed typo

    return render_template('admin/add_product.html', form=form)


@bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            # Handle image upload if a new file was provided
            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products', filename)
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    image.save(image_path)
                    product.image = filename
            
            # Update product fields
            form.populate_obj(product)
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
    
    return render_template('admin/edit_product.html', form=form, product=product)


@bp.route('/delete-product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.products'))
    


@bp.route('/manage-products')
@login_required
def manage_products():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    products = Product.query.all()
    return render_template('admin/manage_products.html', products=products)

@bp.route('/products')
@login_required
def products():
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.order_by(Product.id.desc()).paginate(
        page=page, per_page=10, error_out=False)
    return render_template('admin/products.html', 
                         pagination=pagination,
                         products=pagination.items)