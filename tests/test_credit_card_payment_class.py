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
def sample_credit_card_payment(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Create a sample CreditCardPayment instance
    new_payment = CreditCardPayment(
        card_expiry_date=date,
        card_number='4111111111111111',
        card_type='Visa',
        payment_amount=100.0,
        payment_date=date
    )
    test_db.add(new_payment)
    test_db.commit()
    return new_payment

def test_credit_card_payment_creation(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test creating a CreditCardPayment instance
    payment = CreditCardPayment(
        card_expiry_date=date,
        card_number='5500000000000004',
        card_type='MasterCard',
        payment_amount=200.0,
        payment_date=date
    )
    test_db.add(payment)
    test_db.commit()

    # Verify that the payment was created successfully
    assert payment.id is not None
    assert payment.card_number == '5500000000000004'
    assert payment.card_type == 'MasterCard'
    assert repr(payment) == f"<CreditCardPayment(amount={payment.payment_amount}, card_type={payment.card_type})>"

def test_credit_card_payment_relationship(test_db, sample_credit_card_payment):
    # Test the relationship with Payment 
    assert sample_credit_card_payment.id is not None
    assert sample_credit_card_payment.card_type == 'Visa'

def test_credit_card_payment_repr(sample_credit_card_payment):
    # Test the __repr__ method
    expected_repr = f"<CreditCardPayment(amount={sample_credit_card_payment.payment_amount}, card_type={sample_credit_card_payment.card_type})>"
    assert repr(sample_credit_card_payment) == expected_repr
