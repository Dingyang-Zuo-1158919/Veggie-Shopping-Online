from models.item import Item
from models.order_line import OrderLine
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
def sample_item(test_db):
    # Create a sample Item
    new_item = Item()
    test_db.add(new_item)
    test_db.commit()
    return new_item

def test_item_creation(test_db):
    # Test creating an Item instance
    item = Item()
    test_db.add(item)
    test_db.commit()

    # Verify that the item was created successfully
    assert item.id is not None
    assert repr(item) == "<Item>"

def test_item_relationship(test_db, sample_item):
    # Test the relationship with OrderLine
    order_line = OrderLine(item_number=1, order_id=1, an_item_id=sample_item.id, item_type='Test Item')
    test_db.add(order_line)
    test_db.commit()

    # Verify that the order line refers back to the item
    assert sample_item.order_lines[0] == order_line
    assert order_line.item == sample_item