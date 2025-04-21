from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.products.routes import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')

    from app.cart.routes import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')

    from app.orders.routes import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')

    from app.payments.routes import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

# Import models at the bottom to avoid circular imports
from app import models