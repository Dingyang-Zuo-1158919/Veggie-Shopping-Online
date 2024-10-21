from app.data_query.query_item import paginate
from app.data_query.query_order import cancel_selected_order, get_customer_orders, handle_premade_box, handle_veggie, initialize_order_session, prepare_order_detail
from flask import render_template, request, redirect, session, jsonify, flash, url_for
from app import app

@app.route('/add_to_order', methods=['POST'])
def add_to_order():
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    purchase_type = request.form['purchase_type']
    selected_veggies = request.form.getlist('veggies[]')

    if not item_name or quantity is None or not purchase_type:
        flash('Missing required fields to add an item to the order.', 'danger')
        return jsonify(success=False), 400

    if quantity <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return jsonify(success=False), 400

    initialize_order_session()

    if purchase_type in ['small', 'medium', 'large']:
        return handle_premade_box(item_name, quantity, purchase_type, selected_veggies)
    else:
        return handle_veggie(purchase_type, item_name, quantity)

@app.route('/remove_from_order', methods=['POST'])
def remove_from_order():
    item_id = request.form.get('item_id')
    if not item_id:
        return jsonify(success=False, message='Item ID is missing.'), 400

    # Ensure session order exists
    if 'order' in session:
        session['order'] = [item for item in session['order'] if str(item['item_id']) != item_id]
        session.modified = True  # Mark session as modified to save changes
        # Calculate the total order price after the removal
        total_order_price = sum(item['total_price'] for item in session.get('order', []))
        return jsonify(success=True, total_order_price=total_order_price)  # Return the success status and new total order price
    else:
        return jsonify(success=False, message='No order found in session.'), 400

@app.route('/update_order_quantity', methods=['POST'])
def update_order_quantity():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity', type=int)

    if not item_id or quantity is None or quantity <= 0:
        return jsonify(success=False, message='Invalid item ID or quantity.'), 400

    # Ensure session order exists
    if 'order' in session:
        for item in session['order']:
            if str(item['item_id']) == item_id:
                # Calculate price per unit based on the old total price and old quantity
                old_quantity = item['quantity']  # Keep the old quantity to calculate per unit price
                price_per_unit = item['total_price'] / old_quantity  # Divide by old quantity
                # Update the quantity
                item['quantity'] = quantity
                # Recalculate the total price for the updated quantity
                item['total_price'] = float(quantity) * price_per_unit
                break

        # Calculate the total order price after the update
        total_order_price = sum(item['total_price'] for item in session['order'])
        session.modified = True  # Mark session as modified to save changes
        return jsonify(success=True, total_order_price=total_order_price, total_price=item['total_price'])
    else:
        return jsonify(success=False, message='No order found in session.'), 400

@app.route('/order_list')
def order_list():
    # Fetch user ID from session
    user_id = session.get('user_id')

    if not user_id:
        flash('You must be logged in to view your orders.', 'danger')
        return redirect(url_for('login'))
    
    try:
        # Fetch orders for the customer
        orders = get_customer_orders(user_id)
        # Prepare order details
        order_details = [prepare_order_detail(order) for order in orders]
    except Exception as e:
        flash('Error fetching orders from the database. Please try again later.', 'danger')
        return render_template('error.html'), 500

    # Define the current page for orders and the number of items per page
    try:
        orders_page = int(request.args.get('orders_page', 1))
        if orders_page < 1:
            orders_page = 1
    except ValueError:
        orders_page = 1

    items_per_page = 5

    # Paginate the order details
    orders_paginated, total_orders, total_orders_pages = paginate(order_details, orders_page, items_per_page)

    return render_template('order_list.html', orders=orders_paginated, orders_page=orders_page,
                           total_orders_pages=total_orders_pages,
                           total_orders=total_orders,
                           user_id=user_id)

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    # Get the target page URL from the form
    target_page = request.form.get('target') 

    # Call the helper function to cancel the order
    if not cancel_selected_order(order_id):
        # If there was an issue, redirect back to order management
        return redirect(target_page)

    # On success, redirect to the page displaying all orders
    return redirect(target_page)
