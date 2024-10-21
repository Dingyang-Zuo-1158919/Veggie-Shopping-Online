from models.database import Base
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.veggie import Veggie

@pytest.fixture(scope='module')
def test_db():
    """Create a new database session for a test."""
    engine = create_engine('sqlite:///:memory:')  # Use in-memory SQLite database
    Base.metadata.create_all(engine)  # Create the tables in the test database
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # provide the test database session to the tests

    # Drop the tables after tests are done
    Base.metadata.drop_all(engine)

def test_veggie_creation(test_db):
    """Test creation of a Veggie instance."""
    # Create a Veggie instance
    new_veggie = Veggie(veg_name='Carrot')
    test_db.add(new_veggie)
    test_db.commit()

    # Query the Veggie instance back
    queried_veggie = test_db.query(Veggie).filter_by(veg_name='Carrot').first()

    # Assertions
    assert queried_veggie is not None
    assert queried_veggie.veg_name == 'Carrot'


def test_veggie_repr(test_db):
    """Test the __repr__ method of the Veggie class."""
    new_veggie = Veggie(veg_name='Spinach')
    test_db.add(new_veggie)
    test_db.commit()

    # Test __repr__
    assert repr(new_veggie) == "<Veggie(name=Spinach)>"
