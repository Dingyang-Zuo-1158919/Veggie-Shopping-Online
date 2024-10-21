from models.corporate_customer import CorporateCustomer
from models.credit_card_payment import CreditCardPayment
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
def sample_corporate_customer(test_db):
    # Create a sample CorporateCustomer instance
    new_corporate_customer = CorporateCustomer(
        cust_address='123 Corporate St, Business City',
        cust_balance=1500.0,
        discount_rate=0.15,
        max_credit=300.0,
        min_balance=1200.0,
        username='corp_user',
        first_name='John', last_name='Doe', password='securepassword'
    )
    test_db.add(new_corporate_customer)
    test_db.commit()
    return new_corporate_customer

def test_corporate_customer_creation(test_db):
    # Test creating a CorporateCustomer instance
    corporate_customer = CorporateCustomer(
        cust_address='456 Business Blvd, Commerce Town',
        cust_balance=2000.0,
        discount_rate=0.2,
        max_credit=400.0,
        min_balance=1500.0,
        username='another_corp_user',
        first_name='John', last_name='Doe', password='securepassword'
    )
    test_db.add(corporate_customer)
    test_db.commit()

    # Verify that the corporate customer was created successfully
    assert corporate_customer.id is not None
    assert corporate_customer.cust_address == '456 Business Blvd, Commerce Town'
    assert corporate_customer.cust_balance == 2000.0
    assert corporate_customer.discount_rate == 0.2
    assert corporate_customer.max_credit == 400.0
    assert corporate_customer.min_balance == 1500.0
    assert repr(corporate_customer) == f"<CorporateCustomer(username={corporate_customer.username}, discount_rate={corporate_customer.discount_rate})>"

def test_corporate_customer_relationship(test_db, sample_corporate_customer):
    # Test the relationship with Customer
    assert sample_corporate_customer.id is not None
    assert sample_corporate_customer.cust_balance == 1500.0
    assert sample_corporate_customer.discount_rate == 0.15

def test_corporate_customer_repr(sample_corporate_customer):
    # Test the __repr__ method
    expected_repr = f"<CorporateCustomer(username={sample_corporate_customer.username}, discount_rate={sample_corporate_customer.discount_rate})>"
    assert repr(sample_corporate_customer) == expected_repr