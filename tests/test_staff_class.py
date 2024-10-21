import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base  
from models.staff import Staff  
from models.order import Order  # Import Order for the relationship setup

@pytest.fixture(scope='module')
def test_db():
    """Create a new database session for the test."""
    engine = create_engine('sqlite:///:memory:')  # Use an in-memory SQLite database
    Base.metadata.create_all(engine)  # Create the tables in the test database
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # Provide the session to the tests
    
    # Drop the tables after tests are done
    Base.metadata.drop_all(engine)


def test_staff_creation(test_db):
    """Test creation of a Staff instance."""
    # Create a Staff instance
    new_staff = Staff(username='jdoe', first_name='John', last_name='Doe', password='securepassword', date_joined='2024-01-01', dept_name='Sales')
    test_db.add(new_staff)
    test_db.commit()

    # Query the Staff instance back
    queried_staff = test_db.query(Staff).filter_by(username='jdoe').first()

    # Assertions
    assert queried_staff is not None
    assert queried_staff.dept_name == 'Sales'
    assert queried_staff.date_joined == '2024-01-01'


def test_staff_repr(test_db):
    """Test the __repr__ method of the Staff class."""
    new_staff = Staff(username='asmith', first_name='Joe', last_name='Don', date_joined='2024-01-15', dept_name='Marketing', password='anotherpassword')
    test_db.add(new_staff)
    test_db.commit()

    # Test __repr__
    assert repr(new_staff) == "<Staff(username=asmith, dept=Marketing)>"

    
def test_staff_order_relationship(test_db):
    """Test the relationship between Staff and Order."""
    # Create a Staff instance
    staff_member = Staff(username='mjones', first_name='John', last_name='Donnet', date_joined='2024-01-20', dept_name='Support', password='otherpasswords')
    test_db.add(staff_member)
    test_db.commit()

    # Create an Order instance and associate it with the staff member
    order_date_str = '2024-01-20'
    order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
    order1 = Order(order_date=order_date, order_number=2, order_status='Pending', staff_id=staff_member.id)
    order2 = Order(order_date=order_date, order_number=2, order_status='Pending', staff_id=staff_member.id)
    test_db.add(order1)
    test_db.add(order2)
    test_db.commit()

    # Query the staff member back and check their orders
    queried_staff = test_db.query(Staff).filter_by(username='mjones').first()
    assert len(queried_staff.orders) == 2  # Ensure the staff member has 2 orders
    assert queried_staff.orders[0].order_status == 'Pending'
    assert queried_staff.orders[1].order_status == 'Pending'
