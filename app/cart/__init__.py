# app/cart/__init__.py
from flask import Blueprint

bp = Blueprint('cart', __name__)

from app.cart import routes