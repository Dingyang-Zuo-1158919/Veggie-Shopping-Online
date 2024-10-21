from app.data_query.query_user import get_corporate_customer_by_id, get_customer_by_id, get_staff_by_id
from flask import render_template, redirect, url_for, flash
from app import app

@app.route('/user_profile/<int:user_id>/<string:user_type>', methods=['GET'])
def user_profile(user_id, user_type):
    # Validate the user_type
    if user_type not in ['customer', 'corporate_customer', 'staff']:
        flash('Invalid user type.', 'danger')
        return redirect(url_for('home'))
    user = None

    try:
        # Fetch user information based on user type
        if user_type == 'customer':
            user = get_customer_by_id(user_id)
        elif user_type == 'corporate_customer':
            user = get_corporate_customer_by_id(user_id)
        elif user_type == 'staff':
            user = get_staff_by_id(user_id)
    except Exception as e:
        flash('An error occurred while retrieving the user information.', 'danger')
        return redirect(url_for('home'))
    
    # If the user is not found
    if not user:
        flash('User not found.')
        return redirect(url_for('home'))

    # Pass user data to the template
    return render_template('user_profile.html', user=user, user_type=user_type)

