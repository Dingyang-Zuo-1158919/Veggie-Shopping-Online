from models.item import Item
from models.order import Order
from models.order_line import OrderLine
from datetime import datetime
from models.premade_box import BoxContent
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
def sample_order(test_db):
    date_str = '2024-01-20'
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    new_order = Order(order_date=date, order_number=1, order_status='Pending', customer_id=1)
    test_db.add(new_order)
    test_db.commit()
    return new_order

@pytest.fixture(scope='module')
def sample_item(test_db):
    new_item = Item()  
    test_db.add(new_item)
    test_db.commit()
    return new_item

@pytest.fixture(scope='module')
def sample_box_content(test_db, sample_item):
    new_box_content = BoxContent(premade_box_id=sample_item.id, box_content='Sample Box Content') 
    test_db.add(new_box_content)
    test_db.commit()
    return new_box_content

def test_order_line_initialization(test_db, sample_order, sample_item):
    # Test initializing an OrderLine instance
    order_line = OrderLine(
        item_number=1,
        order_id=sample_order.id,
        an_item_id=sample_item.id,
        item_type='Single Item'
    )
    test_db.add(order_line)
    test_db.commit()

    # Verify that the order line was created correctly
    assert order_line.item_number == 1
    assert order_line.order_id == sample_order.id
    assert order_line.an_item_id == sample_item.id
    assert order_line.item_type == 'Single Item'

def test_order_line_relationships(test_db, sample_order, sample_item):
    # Test relationships
    order_line = OrderLine(
        item_number=2,
        order_id=sample_order.id,
        an_item_id=sample_item.id,
        item_type='Single Item'
    )
    test_db.add(order_line)
    test_db.commit()

    # Verify relationships
    assert order_line.order == sample_order
    assert order_line.item == sample_item

def test_order_line_box_content(test_db, sample_order, sample_item, sample_box_content):
    # Test initializing an OrderLine with BoxContent
    order_line = OrderLine(
        item_number=3,
        order_id=sample_order.id,
        an_item_id=sample_item.id,
        box_content_id=sample_box_content.id,
        item_type='Boxed Item'
    )
    test_db.add(order_line)
    test_db.commit()

    # Verify BoxContent relationship
    assert order_line.box_content == sample_box_content

def test_order_line_repr(test_db, sample_order, sample_item):
    # Test the __repr__ method
    order_line = OrderLine(
        item_number=4,
        order_id=sample_order.id,
        an_item_id=sample_item.id,
        item_type='Another Item'
    )
    assert repr(order_line) == "<OrderLine(item_number=4)>"