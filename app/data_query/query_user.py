from app import db_session
from models.corporate_customer import CorporateCustomer
from models.customer import Customer
from models.person import Person
from models.staff import Staff

def get_customer_by_id(user_id):
    customer = db_session.query(Customer).filter_by(id=user_id).first()
    return customer

def get_corporate_customer_by_id(user_id):
    corporate_customer = db_session.query(CorporateCustomer).filter_by(id=user_id).first()
    return corporate_customer

def get_staff_by_id(user_id):
    staff = db_session.query(Staff).filter_by(id=user_id).first()
    return staff

def fetch_all_customers():
    # Get all corporate customer IDs
    corporate_customer_ids = db_session.query(CorporateCustomer.id).subquery()
    # Fetch all customers excluding those IDs
    return db_session.query(Customer).filter(Customer.id.notin_(corporate_customer_ids)).all()

def fetch_all_corporate_customers():
    return db_session.query(CorporateCustomer).all()

def get_person_by_name(name):
    person = db_session.query(Person).filter_by(username=name).first()
    return person

def get_customer_user_name(customer_id):
    # Retrieve the username of the customer given their ID
    customer = db_session.query(Customer).filter(Customer.id == customer_id).first()
    
    if customer:
        username = customer.customer_username()
        return username  # Return the username from the Customer object
    return None

def get_customer_type(customer_id):
    # Retrieve the type of the customer given their ID
    customer = db_session.query(CorporateCustomer).filter(CorporateCustomer.id == customer_id).first()
    customer_type = 'Corporate' if customer else 'Individual'
    return customer_type  # Return the type from the Customer object

def get_customer_name(customer_id):
    # Fetch the full name of the customer based on their ID
    customer_person = db_session.query(Person).filter(Person.id == customer_id).first()
    return f"{customer_person.first_name} {customer_person.last_name}" if customer_person else "Unknown"