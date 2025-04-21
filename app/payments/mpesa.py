from flask import current_app
import requests
import base64
from datetime import datetime

def format_phone(phone):
    """Format phone number to 2547XXXXXXXX format"""
    if phone.startswith('0'):
        return '254' + phone[1:]
    elif phone.startswith('+'):
        return phone[1:]
    return phone

def get_mpesa_access_token():
    """Get OAuth access token from M-Pesa"""
    consumer_key = current_app.config['MPESA_CONSUMER_KEY']
    consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        response = requests.get(url, auth=(consumer_key, consumer_secret), timeout=30)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        current_app.logger.error(f"M-Pesa token error: {str(e)}")
        return None

def initiate_stk_push(phone, amount, order_id, callback_url):
    """Initiate STK push payment request"""
    try:
        # Format phone number
        phone = format_phone(phone)
        if len(phone) != 12 or not phone.startswith('254'):
            raise ValueError("Invalid phone number format")
        
        # Get access token
        access_token = get_mpesa_access_token()
        if not access_token:
            raise ValueError("Could not get access token")
        
        # Prepare request
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Generate password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        passkey = current_app.config['MPESA_PASSKEY']
        business_shortcode = current_app.config['MPESA_BUSINESS_SHORTCODE']
        password = base64.b64encode(
            f"{business_shortcode}{passkey}{timestamp}".encode()
        ).decode()
        
        # Prepare payload
        payload = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),
            "PartyA": phone,
            "PartyB": business_shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url or current_app.config['MPESA_CALLBACK_URL'],
            "AccountReference": f"BFL{order_id}",
            "TransactionDesc": f"Payment for order #{order_id}"
        }
        
        # Make request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Log and return response
        current_app.logger.info(f"M-Pesa STK Push response: {response.json()}")
        return response.json()
        
    except Exception as e:
        current_app.logger.error(f"M-Pesa STK Push failed: {str(e)}")
        return {
            'ResponseCode': '1',
            'ResponseDescription': str(e)
        }