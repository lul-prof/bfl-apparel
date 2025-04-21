from flask import render_template
from flask_login import login_required
from app.main import bp
from app.models import Product

@bp.route('/')
@bp.route('/index')
def index():
    featured_products = Product.query.limit(4).all()
    return render_template('index.html', title='Home', featured_products=featured_products)