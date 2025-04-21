# app/orders/__init__.py
from flask import Blueprint

bp = Blueprint('orders', __name__)

from app.orders import routes