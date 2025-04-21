# app/products/__init__.py
from flask import Blueprint

bp = Blueprint('products', __name__)

from app.products import routes