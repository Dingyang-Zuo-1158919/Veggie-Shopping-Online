import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.unit_price_veggie import UnitPriceVeggie  


@pytest.fixture(scope='module')
def test_db():
    """Create a new database session for a test."""
    engine = create_engine('sqlite:///:memory:')  # Use an in-memory SQLite database
    Base.metadata.create_all(engine)  # Create the tables in the test database
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session  # Provide the session to the tests
    
    # Drop the tables after tests are done
    Base.metadata.drop_all(engine)


def test_unit_price_veggie_creation(test_db):
    """Test creation of a UnitPriceVeggie instance."""
    # Create a UnitPriceVeggie instance
    new_unit_price_veggie = UnitPriceVeggie(veg_name='Tomato', quantity=10.0, price_per_unit=1.5)
    test_db.add(new_unit_price_veggie)
    test_db.commit()

    # Query the UnitPriceVeggie instance back
    queried_veggie = test_db.query(UnitPriceVeggie).filter_by(veg_name='Tomato').first()

    # Assertions
    assert queried_veggie is not None
    assert queried_veggie.veg_name == 'Tomato'
    assert queried_veggie.quantity == 10.0
    assert queried_veggie.price_per_unit == 1.5


def test_calculate_unit_price(test_db):
    """Test the calculate_unit_price method."""
    unit_price_veggie = UnitPriceVeggie(veg_name='Cucumber', quantity=5.0, price_per_unit=2.0)
    unit_price = unit_price_veggie.calculate_unit_price(unit_price_veggie.quantity, unit_price_veggie.price_per_unit)

    # Assertions
    assert unit_price == 10.0  # 5.0 * 2.0 = 10.0


def test_unit_price_veggie_repr(test_db):
    """Test the __repr__ method of the UnitPriceVeggie class."""
    new_unit_price_veggie = UnitPriceVeggie(veg_name='Lettuce', quantity=3.0, price_per_unit=0.75)
    test_db.add(new_unit_price_veggie)
    test_db.commit()

    # Test __repr__
    assert repr(new_unit_price_veggie) == "<UnitPriceVeggie(name=Lettuce, quantity=3.0)>"
