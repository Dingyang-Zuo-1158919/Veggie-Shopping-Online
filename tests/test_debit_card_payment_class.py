from models.debit_card_payment import DebitCardPayment
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
def sample_payment(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Create a sample Payment instance
    new_payment = Payment(payment_amount=100.0, payment_date=date)
    test_db.add(new_payment)
    test_db.commit()
    return new_payment

def test_debit_card_payment_creation(test_db, sample_payment):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test creating a DebitCardPayment instance
    debit_card_payment = DebitCardPayment(
        payment_amount=75.0, 
        payment_date=date, 
        bank_name='Bank of Testing', 
        debit_card_number='1234567890123456'
    )
    test_db.add(debit_card_payment)
    test_db.commit()

    # Verify that the debit card payment was created successfully
    assert debit_card_payment.id is not None
    assert debit_card_payment.bank_name == 'Bank of Testing'
    assert debit_card_payment.debit_card_number == '1234567890123456'
    assert repr(debit_card_payment) == f"<DebitCardPayment(amount={debit_card_payment.payment_amount}, bank_name={debit_card_payment.bank_name})>"

def test_debit_card_payment_relationship(test_db, sample_payment):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # Test the relationship with Payment
    debit_card_payment = DebitCardPayment(
        payment_amount=50.0, 
        payment_date=date, 
        bank_name='Test Bank', 
        debit_card_number='6543210987654321'
    )
    test_db.add(debit_card_payment)
    test_db.commit()

    # Verify that the debit card payment refers back to the payment
    assert debit_card_payment.payment_amount == 50.0
    assert debit_card_payment.payment_date == datetime.strptime('2024-01-20', '%Y-%m-%d').date()
    assert debit_card_payment.bank_name == 'Test Bank'
    assert debit_card_payment.debit_card_number == '6543210987654321'