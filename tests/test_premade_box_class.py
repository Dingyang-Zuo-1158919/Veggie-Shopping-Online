import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base 
from models.veggie import Veggie
from models.premade_box import PremadeBox, BoxContent  

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

def test_create_premade_box(test_db):
    """Test creating a PremadeBox instance."""
    premade_box = PremadeBox(box_size='medium', num_of_boxes=5)
    test_db.add(premade_box)
    test_db.commit()

    # Retrieve the box from the database
    box_in_db = test_db.query(PremadeBox).filter_by(box_size='medium').first()
    assert box_in_db is not None
    assert box_in_db.num_of_boxes == 5


def test_calculate_box_price(test_db):
    """Test the price calculation of a PremadeBox."""
    premade_box = PremadeBox(box_size='large', num_of_boxes=2)
    test_db.add(premade_box)
    test_db.commit()

    price = premade_box.calculate_box_price(premade_box.box_size, premade_box.num_of_boxes)
    assert price == 36  # 18 * 2


def test_add_veggie_to_box_content(test_db):
    """Test adding a veggie to BoxContent."""
    premade_box = PremadeBox(box_size='medium', num_of_boxes=3)
    box_content = BoxContent(premade_box=premade_box, box_content='')
    test_db.add(premade_box)
    test_db.add(box_content)
    test_db.commit()

    veggie = Veggie(veg_name='Carrot')  
    box_content.add_veggie(veggie)
    test_db.commit()

    # Verify that the veggie was added
    assert 'Carrot' in box_content.box_content

def test_remove_veggie_from_box_content(test_db):
    """Test removing a veggie from BoxContent."""
    premade_box = PremadeBox(box_size='medium', num_of_boxes=3)
    box_content = BoxContent(premade_box=premade_box, box_content='Carrot,Tomato')
    test_db.add(premade_box)
    test_db.add(box_content)
    test_db.commit()

    veggie_to_remove = Veggie(veg_name='Carrot')  
    box_content.remove_veggie(veggie_to_remove)
    test_db.commit()

    assert box_content.box_content == 'Tomato'  # Carrot should be removed



