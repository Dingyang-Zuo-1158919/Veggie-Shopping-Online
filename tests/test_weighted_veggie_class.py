import itertools
from models.database import Base
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.weighted_veggie import WeightedVeggie

# Set up a test database
@pytest.fixture(scope='module')
def test_db():
    # Create an in-memory SQLite database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Provide the session to the tests

    # Drop the tables after tests are done
    Base.metadata.drop_all(engine)
    
unique_id_counter = itertools.count(1)  # Start counting from 1
@pytest.fixture()
def weighted_veggie(test_db):
    veggie_id = next(unique_id_counter) 
    # Create a sample WeightedVeggie instance
    veggie = WeightedVeggie(id=veggie_id, veg_name='Carrot', weight=2.0, weight_per_kilo=3.5)
    test_db.add(veggie)
    test_db.commit()
    return veggie

def test_weighted_veggie_attributes(weighted_veggie):
    assert weighted_veggie.veg_name == 'Carrot'
    assert weighted_veggie.weight == 2.0
    assert weighted_veggie.weight_per_kilo == 3.5

def test_calculate_weight_price(weighted_veggie):
    expected_price = weighted_veggie.calculate_weight_price(weighted_veggie.weight, weighted_veggie.weight_per_kilo)
    assert expected_price == 7.0  # 2.0 * 3.5

def test_repr(weighted_veggie):
    expected_repr = "<WeightedVeggie(name=Carrot, weight=2.0)>"
    assert repr(weighted_veggie) == expected_repr
