from app.data_query.query_item import fetch_all_premade_boxes, fetch_all_veggies, paginate
from app.data_query.query_order import calculate_total_order_price
from app.data_query.query_user import get_corporate_customer_by_id, get_customer_by_id, get_person_by_name, get_staff_by_id
from flask import render_template, request, redirect, url_for, flash, session
from app import app
from werkzeug.security import check_password_hash

@app.route('/')
def home():
    user_id = session.get('user_id')
    selected_type = request.args.get('type', 'veggies')
    user_type = session.get('user_type')
    order = session.get('order', [])
    # Calculate the total order price
    total_order_price = calculate_total_order_price(order)

    try:
        # Fetch all veggies according to user role
        all_veggies = fetch_all_veggies(user_type)
        # Fetch all premade box stock according to user role
        premade_box_stock = fetch_all_premade_boxes(user_type)
    except Exception as e:
        flash('Error fetching data from the database. Please try again later.', 'danger')
        return render_template('error.html'), 500

    # Validate veggies page input
    try:
        veggies_page = int(request.args.get('veggies_page', 1))
        if veggies_page < 1:
            veggies_page = 1  # Ensure page number is at least 1
    except ValueError:
        veggies_page = 1  # Default to page 1 on invalid input

    # Define the number of items per page
    items_per_page = 9

    # Use the paginate function for veggies
    veggies_paginated, total_veggies, total_veggies_pages = paginate(all_veggies, veggies_page, items_per_page)

    return render_template('home.html', 
                           selected_type=selected_type, 
                           veggies_paginated=veggies_paginated,
                           veggies_page=veggies_page, 
                           total_veggies_pages=total_veggies_pages,
                           user_type=user_type,
                           all_veggies=all_veggies, 
                           total_order_price=total_order_price, 
                           user_id=user_id,
                           premade_box_stock=premade_box_stock)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('login.html')

        try:
            user = get_person_by_name(username)
        except Exception as e:
            flash('Error accessing the database. Please try again later.', 'danger')
            return render_template('login.html')
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username

            try:
                customer = get_customer_by_id(user.id)
                corporate_customer = get_corporate_customer_by_id(user.id)
                staff = get_staff_by_id(user.id)
            except Exception as e:
                flash('Error accessing user details. Please try again later.', 'danger')
                return redirect(url_for('login'))

            # Determine user type based on subclass
            if staff:
                session['user_type'] = 'staff'
            elif corporate_customer:
                session['user_type'] = 'corporate_customer'
            elif customer:
                session['user_type'] = 'customer'

            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))
