from models.customer import Customer
from models.order import Order
from models.payment import Payment
import pytest
from datetime import datetime
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
    # Create a sample Customer instance
    new_customer = Customer(username='testuser', first_name='John', last_name='Doe', password='securepassword', cust_address='123 Test St', cust_balance=150.0)
    test_db.add(new_customer)
    test_db.commit()
    return new_customer

def test_customer_creation(test_db):
    # Test creating a Customer instance
    customer = Customer(username='newuser', first_name='John', last_name='Doe', password='securepassword', cust_address='456 New St', cust_balance=200.0)
    test_db.add(customer)
    test_db.commit()

    # Verify that the customer was created successfully
    assert customer.id is not None
    assert customer.username == 'newuser'
    assert customer.cust_address == '456 New St'
    assert customer.cust_balance == 200.0
    assert repr(customer) == f"<Customer(username={customer.username}, balance={customer.cust_balance})>"

def test_customer_relationships(test_db, sample_customer):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test the relationship with Payment
    payment = Payment(payment_amount=50.0, payment_date=date, customer=sample_customer)
    test_db.add(payment)
    test_db.commit()

    assert len(sample_customer.payments) == 1
    assert sample_customer.payments[0].payment_amount == 50.0

    # Test the relationship with Order
    order = Order(order_number=1, order_status='Pending', order_date=date, customer_id=sample_customer.id)
    test_db.add(order)
    test_db.commit()

    assert len(sample_customer.orders) == 1
    assert sample_customer.orders[0].order_number == 1

def test_customer_username_method(sample_customer):
    # Test the customer_username method
    assert sample_customer.username == 'testuser'
