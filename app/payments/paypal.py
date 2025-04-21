import paypalrestsdk
from flask import current_app

def configure_paypal():
    paypalrestsdk.configure({
        "mode": current_app.config['PAYPAL_MODE'],
        "client_id": current_app.config['PAYPAL_CLIENT_ID'],
        "client_secret": current_app.config['PAYPAL_CLIENT_SECRET']
    })

def create_payment(amount, return_url, cancel_url, description):
    configure_paypal()
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "USD"
            },
            "description": description
        }]
    })
    
    if payment.create():
        return payment
    return None

def execute_payment(payment_id, payer_id):
    configure_paypal()
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return payment
    return None