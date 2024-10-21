from datetime import datetime
from app.data_query.query_item import paginate
from app.data_query.query_order import get_all_orders, prepare_order_detail, update_order_status
from app.data_query.query_sales_data import fetch_sales_data
from app.data_query.query_user import fetch_all_corporate_customers, fetch_all_customers
from flask import render_template, request, session, redirect, url_for, flash
from app import app

@app.route('/manage_order', methods=['GET','POST'])
def manage_order():
    # Fetch staff ID from session
    staff_id = session.get('user_id')

    if not staff_id:
        return redirect(url_for('login'))  # Redirect to login if no staff_id

    # Fetch all orders
    try:
        orders = get_all_orders()
    except Exception as e:
        flash(f"Error fetching orders: {e}",'danger')
        return render_template('error.html', message="Could not fetch orders at this time.")

    # Prepare order details
    try:
        order_details = [prepare_order_detail(order) for order in orders]
    except Exception as e:
        flash(f"Error preparing order details: {e}", 'danger')
        return render_template('error.html', message="Could not prepare order details.")

    # Define and validate the current page
    try:
        orders_page = int(request.args.get('orders_page', 1))
        if orders_page < 1:
            orders_page = 1
    except ValueError:
        orders_page = 1

    items_per_page = 5

    # Paginate the order details
    orders_paginated, total_orders, total_orders_pages = paginate(order_details, orders_page, items_per_page)

    return render_template('manage_order.html', orders=orders_paginated, orders_page=orders_page,
                           total_orders_pages=total_orders_pages,
                           total_orders=total_orders,
                           user_id=staff_id)

@app.route('/staff/review_order/<int:order_id>', methods=['POST'])
def review_order(order_id):
    # Fetch staff id from session
    staff_id = session.get('user_id')
    if not staff_id:
        return redirect(url_for('login'))
    
    # Call the helper function to update the order status
    if not update_order_status(order_id, staff_id):
        # If there was an issue, redirect back to order management
        return redirect(url_for('manage_order'))

    # On success, redirect to the page displaying all orders
    return redirect(url_for('manage_order'))

@app.route('/staff/manage_customer', methods=['GET'])
def manage_customer():
    try:
        # Fetch all customers and corporate customers
        customers = fetch_all_customers()
        corporate_customers = fetch_all_corporate_customers()
    except Exception as e:
        flash(f"Error fetching customers: {e}",'danger')
        return render_template('error.html', message="Could not fetch customers at this time.")

    # Create a list of corporate customer IDs
    corporate_customer_ids = [c.id for c in corporate_customers]

    # Combine both lists for rendering
    all_customers = customers + corporate_customers
    
    return render_template('manage_customer.html', customers=all_customers, corporate_customer_ids=corporate_customer_ids)

@app.route('/sales_performance', methods=['GET'])
def sales_performance():
    # Get current year to pass to the template
    current_year = datetime.now().year

    # Get the user's choice: year or month
    view_choice = request.args.get('year_or_month')
    
    # If the user has selected a month and year
    selected_month = request.args.get('month', type=int)
    selected_year = request.args.get('year', type=int)

    sales_data = None

    try:
        if view_choice == 'year' and selected_year:
            # Fetch sales data for the selected year
            sales_data = fetch_sales_data(None, selected_year)
        elif view_choice == 'month' and selected_year and selected_month:
            # Fetch sales data for the selected month and year
            sales_data = fetch_sales_data(selected_month, selected_year)
    except Exception as e:
        flash(f"Error fetching sales data: {e}", 'danger')
        return render_template('error.html', message="Could not fetch sales data.")

    # Fetch current week's, month's and year's sales data (default/current)
    try:
        current_sales_data = fetch_sales_data()
    except Exception as e:
        flash(f"Error fetching current sales data: {e}", 'danger')
        current_sales_data = {}

    return render_template('sales_performance.html', sales_data=sales_data, 
                           view_choice=view_choice, current_year=current_year, 
                           current_sales_data=current_sales_data)