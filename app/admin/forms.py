from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('T-Shirts', 'T-Shirts'),
        ('Hoodies', 'Hoodies'),
        ('Pants', 'Pants'),
        ('Accessories', 'Accessories')
    ], validators=[DataRequired()])
    image = FileField('Product Image', validators=[DataRequired()])
    submit = SubmitField('Add Product')