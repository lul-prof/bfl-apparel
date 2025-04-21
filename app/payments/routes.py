from flask import abort, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Order
from .mpesa import initiate_stk_push
from .paypal import create_payment, execute_payment
from app.payments import bp

@bp.route('/process/<int:order_id>', methods=['GET', 'POST'])
@login_required
def process_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You cannot pay for this order!')
        return redirect(url_for('main.index'))
    
    if order.payment_status != 'Pending':
        flash('This order has already been paid for!')
        return redirect(url_for('orders.order_details', order_id=order.id))
    
    phone = request.args.get('phone', '')
    
    if order.payment_method == 'mpesa':
        response = initiate_stk_push(
            phone=phone,
            amount=order.total_amount,
            order_id=order.id,
            callback_url=url_for('payments.mpesa_callback', _external=True)
        )
        
        if response and 'ResponseCode' in response and response['ResponseCode'] == '0':
            order.payment_status = 'Processing'
            db.session.commit()
            flash('MPesa payment initiated. Please check your phone to complete the payment.')
            return redirect(url_for('orders.order_details', order_id=order.id))
        else:
            flash('Failed to initiate MPesa payment. Please try again.')
            return redirect(url_for('orders.checkout'))
    
    elif order.payment_method == 'paypal':
        payment = create_payment(
            amount=order.total_amount,
            return_url=url_for('payments.paypal_success', order_id=order.id, _external=True),
            cancel_url=url_for('payments.paypal_cancel', order_id=order.id, _external=True),
            description=f"Payment for order #{order.id}"
        )
        
        if payment:
            for link in payment.links:
                if link.method == 'REDIRECT':
                    return redirect(link.href)
        
        flash('Failed to initiate PayPal payment. Please try again.')
        return redirect(url_for('orders.checkout'))
    
    flash('Invalid payment method!')
    return redirect(url_for('orders.checkout'))

@bp.route('/paypal/success/<int:order_id>')
@login_required
def paypal_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('You cannot pay for this order!')
        return redirect(url_for('main.index'))
    
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    
    payment = execute_payment(payment_id, payer_id)
    if payment and payment.state == 'approved':
        order.payment_status = 'Completed'
        order.status = 'Processing'
        db.session.commit()
        flash('Payment completed successfully!')
    else:
        flash('Payment failed. Please try again.')
    
    return redirect(url_for('orders.order_details', order_id=order.id))

@bp.route('/paypal/cancel/<int:order_id>')
@login_required
def paypal_cancel(order_id):
    flash('Payment was cancelled.')
    return redirect(url_for('orders.order_details', order_id=order_id))

# In app/payments/routes.py
@bp.route('/process/mpesa/<int:order_id>')
@login_required
def process_mpesa(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Verify order ownership
    if order.user_id != current_user.id:
        flash('You can only pay for your own orders', 'danger')
        return redirect(url_for('main.index'))
    
    # Verify payment method
    if order.payment_method != 'mpesa':
        flash('This order is not for M-Pesa payment', 'danger')
        return redirect(url_for('orders.order_details', order_id=order.id))
    
    # Process M-Pesa payment
    try:
        response = initiate_stk_push(
            phone=order.mpesa_phone,
            amount=order.total_amount,
            order_id=order.id,
            callback_url=url_for('payments.mpesa_callback', _external=True)
        )
        
        if response and response.get('ResponseCode') == '0':
            order.payment_status = 'Processing'
            db.session.commit()
            flash('M-Pesa payment initiated. Please complete on your phone.', 'success')
        else:
            flash('Failed to initiate M-Pesa payment. Please try again.', 'danger')
    
    except Exception as e:
        db.session.rollback()
        flash('Payment processing error. Please try again.', 'danger')
        current_app.logger.error(f"M-Pesa processing error: {str(e)}")
    
    return redirect(url_for('orders.order_details', order_id=order.id))

@bp.route('/process/paypal/<int:order_id>')
@login_required
def process_paypal(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    
    # Process PayPal payment
    payment = create_payment(
        amount=order.total_amount,
        return_url=url_for('payments.paypal_success', order_id=order.id, _external=True),
        cancel_url=url_for('payments.paypal_cancel', order_id=order.id, _external=True),
        description=f"BFL Apparel Order #{order.id}"
    )
    
    if payment:
        for link in payment.links:
            if link.method == 'REDIRECT':
                return redirect(link.href)
    
    flash('Failed to initiate PayPal payment. Please try again.', 'danger')
    return redirect(url_for('orders.checkout'))

@bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    current_app.logger.info(f"MPesa callback received: {request.json}")
    return '', 200