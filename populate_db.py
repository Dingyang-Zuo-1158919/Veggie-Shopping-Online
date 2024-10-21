from models.pack_veggie import PackVeggie
from models.person import Person
from models.unit_price_veggie import UnitPriceVeggie
from models.weighted_veggie import WeightedVeggie
from werkzeug.security import generate_password_hash  
from models.corporate_customer import CorporateCustomer
from models.customer import Customer
from models.premade_box import PremadeBox
from models.staff import Staff
from models.veggie import Veggie
from app import db_session

def populate_database():
    # Sample data for Veggies
    veggies_data = [
        {'veg_name': 'Carrot'},
        {'veg_name': 'Tomato'},
        {'veg_name': 'Cucumber'},
        {'veg_name': 'Bell Pepper'},
        {'veg_name': 'Spinach'},
        {'veg_name': 'Kale'},
        {'veg_name': 'Broccoli'},
        {'veg_name': 'Zucchini'},
        {'veg_name': 'Eggplant'},
        {'veg_name': 'Radish'},
        {'veg_name': 'Potato'},
        {'veg_name': 'Sweet Potato'},
        {'veg_name': 'Onion'},
        {'veg_name': 'Garlic'},
        {'veg_name': 'Lettuce'}
    ]

    # Prices for different types
    pack_price = 10
    unit_price = 4
    weight_price = 2

    # Sample data for Users with roles
    users_data = [
        {'first_name': 'Alice', 'last_name': 'Johnson', 'username': 'alice', 'password': 'UserPassword_123', 'role': 'customer'},
        {'first_name': 'Bob', 'last_name': 'Smith', 'username': 'bob', 'password': 'UserPassword_123', 'role': 'corporate'},
        {'first_name': 'Charlie', 'last_name': 'Brown', 'username': 'charlie', 'password': 'UserPassword_123', 'role': 'staff'},
    ]

    # Sample data for PremadeBox
    premade_boxes = [
        PremadeBox(box_size='small', num_of_boxes=100),
        PremadeBox(box_size='medium', num_of_boxes=150),
        PremadeBox(box_size='large', num_of_boxes=50)
    ]

    # Add PremadeBox instances to the session
    for box in premade_boxes:
        db_session.add(box)

    # Add Veggies to the database
    for veggie in veggies_data:
        # Add PackVeggie entry
        pack_veggie = PackVeggie(veg_name=veggie['veg_name'], pack_quantity=1000, price_per_pack=pack_price)
        db_session.add(pack_veggie)

        # Add UnitPriceVeggie entry
        unit_price_veggie = UnitPriceVeggie(veg_name=veggie['veg_name'], quantity=1000, price_per_unit=unit_price)
        db_session.add(unit_price_veggie)

        # Add WeightedVeggie entry
        weighted_veggie = WeightedVeggie(veg_name=veggie['veg_name'], weight=1000, weight_per_kilo=weight_price)
        db_session.add(weighted_veggie)

    # Add Users to the database based on their roles
    for user in users_data:
        # Create Customer or CorporateCustomer based on the role
        if user['role'] == 'customer':
            new_customer = Customer(
                first_name=user['first_name'],
                last_name=user['last_name'],
                password=generate_password_hash(user['password']),  # Hash the password
                username=user['username'],
                cust_address='Address for ' + user['username'],  # Example address
                cust_balance=100.0,
                max_owing=50.0
            )
            db_session.add(new_customer)
        
        elif user['role'] == 'corporate':
            new_corporate_customer = CorporateCustomer(
                first_name=user['first_name'],
                last_name=user['last_name'],
                password=generate_password_hash(user['password']),  # Hash the password
                username=user['username'],
                cust_address='Corporate Address for ' + user['username'],  # Example address
                cust_balance=300.0,
                max_owing=100.0,
                discount_rate=10.0,
                max_credit=500.0,
                min_balance=50.0
            )
            db_session.add(new_corporate_customer)

        elif user['role'] == 'staff':
            new_staff = Staff(
                first_name=user['first_name'],
                last_name=user['last_name'],
                password=generate_password_hash(user['password']),  # Hash the password
                username=user['username'],
                date_joined='2024-09-29',
                dept_name='Order'
            )
            db_session.add(new_staff)

    # Commit the changes to the database
    db_session.commit()

if __name__ == "__main__":
    populate_database()
