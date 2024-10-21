from models.customer import Customer
from models.order import Order
from models.payment import Payment
from datetime import datetime
from models.staff import Staff
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base

# Create a SQLite in-memory database for testing
@pytest.fixture(scope='module')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)  # Create tables
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

    # Drop the tables after tests are done
    session.close()  # Close the session
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='module')
def sample_customer(test_db):
    new_customer = Customer(username='jd', first_name='Jo', last_name='Do', password='securepassword', cust_address='abc')  
    test_db.add(new_customer)
    test_db.commit()
    return new_customer

@pytest.fixture(scope='module')
def sample_staff(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    new_staff = Staff(username='jdoe', first_name='John', last_name='Doe', password='securepassword', date_joined=date, dept_name='Sales')  
    test_db.add(new_staff)
    test_db.commit()
    return new_staff

@pytest.fixture(scope='module')
def sample_payment(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    new_payment = Payment(payment_amount=100.0, payment_date=date, customer_id=1)  # Ensure a valid customer ID
    test_db.add(new_payment)
    test_db.commit()
    return new_payment

def test_order_initialization(test_db, sample_customer, sample_staff, sample_payment):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test initializing an Order instance
    new_order = Order(
        order_date=date,
        order_number=1,
        order_status='Pending',
        customer_id=sample_customer.id,
        staff_id=sample_staff.id,
        payment_id=sample_payment.id
    )
    test_db.add(new_order)
    test_db.commit()

    # Verify that the order was created correctly
    assert new_order.order_number == 1
    assert new_order.order_status == 'Pending'
    assert new_order.customer_id == sample_customer.id
    assert new_order.staff_id == sample_staff.id
    assert new_order.payment_id == sample_payment.id

def test_order_relationships(test_db, sample_customer, sample_staff, sample_payment):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test relationships
    new_order = Order(
        order_date=date,
        order_number=2,
        order_status='Completed',
        customer_id=sample_customer.id,
        staff_id=sample_staff.id,
        payment_id=sample_payment.id
    )
    test_db.add(new_order)
    test_db.commit()

    # Verify relationships
    assert new_order.customer == sample_customer
    assert new_order.staff == sample_staff
    assert new_order.payment == sample_payment

def test_order_repr(test_db, sample_customer, sample_staff, sample_payment):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test the __repr__ method
    new_order = Order(
        order_date=date,
        order_number=3,
        order_status='Shipped',
        customer_id=sample_customer.id,
        staff_id=sample_staff.id,
        payment_id=sample_payment.id
    )
    assert repr(new_order) == "<Order(order_number=3, status=Shipped)>"