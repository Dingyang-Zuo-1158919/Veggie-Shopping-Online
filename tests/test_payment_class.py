from models.customer import Customer
from models.payment import Payment
from datetime import datetime
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
    # Create a sample customer for testing
    new_customer = Customer(first_name='John', last_name='Doe', username='johndoe', password='securepassword', cust_address='abc')
    test_db.add(new_customer)
    test_db.commit()
    return new_customer


def test_payment_creation(test_db, sample_customer):
    # Test creating a new Payment
    payment_date_str = '2024-01-20'
    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
    new_payment = Payment(payment_amount=100.0, payment_date=payment_date, customer_id=sample_customer.id)
    test_db.add(new_payment)
    test_db.commit()

    # Retrieve the payment from the database
    retrieved_payment = test_db.query(Payment).filter_by(payment_amount=100.0).first()

    assert retrieved_payment is not None
    assert retrieved_payment.payment_amount == 100.0
    assert retrieved_payment.payment_date.strftime('%Y-%m-%d') == '2024-01-20'
    assert retrieved_payment.customer_id == sample_customer.id

def test_payment_missing_fields(test_db, sample_customer):
    # Test creating a Payment with missing required fields
    payment_date_str = '2024-01-20'
    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
    incomplete_payment = Payment(payment_date=payment_date, customer_id=sample_customer.id)  # Missing amount

    with pytest.raises(Exception):  
        test_db.add(incomplete_payment)
        test_db.commit()