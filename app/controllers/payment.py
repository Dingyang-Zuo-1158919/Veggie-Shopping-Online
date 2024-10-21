from app.data_query.query_order import add_order_lines, create_order, get_customer_and_apply_discount, update_stock_quantity
from app.data_query.query_payment import process_account_payment, process_card_payment
from flask import render_template, request, redirect, url_for, session, flash
from app import app

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Fetch user role and customer information
    user_type = session.get('user_type')
    user_id = session.get('user_id')

    if request.method == 'POST':
        payment_method = request.form['payment_method']
        total_order_price = request.form['total_order_price']
        order = session.get('order', [])
        total_quantity = request.form['total_quantity']
        # Before processing payment, check the latest stock quantity in database again
        # Call Update stock function to update stock quantity for all order items
        stock_check_result = update_stock_quantity()

        if stock_check_result == False:
            # Return to home page to let user revise the shopping cart
            flash('No enough stock for some item, please revise your order accordingly!', 'danger')
            return redirect(url_for('home'))

        if not payment_method:  # Ensure payment method is provided
            flash('Please select a payment method.')
            return redirect(url_for('checkout'))
        
        # Fetch customer and apply discount if corporate customer
        customer, total_order_price = get_customer_and_apply_discount(user_type, user_id, total_order_price)
        if not customer:
            flash('Invalid user type.', 'danger')
            return redirect(url_for('checkout'))

        # Create new order
        new_order = create_order(user_id, total_quantity)

        # Add order lines
        add_order_lines(new_order.id, order)

        # Process payment
        if payment_method in ['credit_card', 'debit_card']:
            process_card_payment(user_id, payment_method, total_order_price, new_order)
        elif payment_method == 'account':
            if not process_account_payment(user_type, customer, total_order_price, new_order):
                return redirect(url_for('checkout', total_order_price=total_order_price))

        # Clear order from session after successful payment
        session.pop('order', None)
        flash('Paid successfully.', 'success')
        return redirect(url_for('order_list'))

    # GET method
    elif request.method == 'GET':
        # Get the order details and total price to pass to the template
        order = session.get('order', [])
        # Get total_order_price from query parameters
        total_order_price_str = request.args.get('total_order_price')
        
        # Convert total_order_price to float
        try:
            total_order_price = float(total_order_price_str)
        except ValueError:
            flash('Invalid total order price format.')
            return redirect(url_for('home'))
        
        # Check customer role to apply discount for corporate customer
        if user_type == 'corporate_customer':
            total_order_price = total_order_price * 0.9
        # Get total order items quantity
        total_quantity = sum(item['quantity'] for item in order) 

        return render_template('checkout.html', order=order, total_order_price=total_order_price, total_quantity=total_quantity)
