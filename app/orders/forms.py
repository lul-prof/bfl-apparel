from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Regexp

class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired()],
                                  render_kw={"placeholder": "Enter your complete shipping address"})
    
    payment_method = RadioField('Payment Method', 
                              choices=[
                                  ('mpesa', 'M-Pesa Mobile Money'),
                                  ('paypal', 'PayPal')
                              ],
                              default='mpesa',
                              validators=[DataRequired()])
    
    phone = StringField('M-Pesa Phone Number',
                       validators=[Optional(),
                                  Regexp(r'^254[17]\d{8}$', 
                                         message="Enter valid M-Pesa number (254XXXXXXXXX)")],
                       render_kw={"placeholder": "2547XXXXXXXX"})
    
    submit = SubmitField('Place Order', render_kw={"class": "btn btn-dark w-100 py-3"})