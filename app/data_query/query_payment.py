from datetime import datetime, timedelta
from flask import request, flash
from app import db_session
from models.credit_card_payment import CreditCardPayment
from models.debit_card_payment import DebitCardPayment
from models.payment import Payment

def process_card_payment(user_id, payment_method, total_order_price, new_order):
    # Convert user input expiry date
    card_expiry_date = convert_card_expiry_date(request.form['card_expiry_date'])
    # Add to database according to card type 
    if payment_method == 'credit_card':
        card_number = request.form.get('credit_card_number')
        new_payment = CreditCardPayment(
            payment_amount=total_order_price,
            payment_date=datetime.now(),
            customer_id=user_id,
            card_number=card_number,
            card_expiry_date=card_expiry_date,
            card_type='Credit Card'
        )
    else:  # Debit card
        bank_name = request.form.get('bank_name')
        debit_card_number = request.form['debit_card_number']
        new_payment = DebitCardPayment(
            payment_amount=total_order_price,
            payment_date=datetime.now(),
            customer_id=user_id,
            debit_card_number=debit_card_number,
            bank_name=bank_name
        )

    db_session.add(new_payment)
    db_session.commit()
    # Update order with payment information
    finalize_order_payment(new_order, new_payment.id, 'Paid by Card')


def process_account_payment(user_type, customer, total_order_price, new_order):
    if not check_account_balance(user_type, customer, total_order_price):
        flash("Insufficient funds to complete the order.", 'danger')
        return False
    
    customer.cust_balance -= float(total_order_price)
    db_session.commit()

    new_payment = Payment(
        payment_amount=total_order_price,
        payment_date=datetime.now(),
        customer_id=customer.id,
    )
    db_session.add(new_payment)
    db_session.commit()

    finalize_order_payment(new_order, new_payment.id, 'Paid by Account Balance')
    return True

def check_account_balance(user_type, customer, total_order_price):
    if user_type == 'customer' and (customer.cust_balance - float(total_order_price) + customer.max_owing) < 0:
        return False
    if user_type == 'corporate_customer' and (customer.cust_balance - float(total_order_price) + customer.max_credit) < 0:
        return False
    return True

def finalize_order_payment(new_order, payment_id, order_status):
    new_order.payment_id = payment_id
    new_order.order_status = order_status
    db_session.commit()

def convert_card_expiry_date(card_expiry_date_str):
    try:
        month, year = card_expiry_date_str.split('/')
        year = int(year) + 2000
        card_expiry_date = datetime(year, int(month), 1).replace(day=1) + timedelta(days=31)
        return card_expiry_date.replace(day=1) - timedelta(days=1)
    except ValueError:
        return None