from models.pack_veggie import PackVeggie
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
def sample_pack_veggie(test_db):
    # Create a sample PackVeggie for testing
    new_pack_veggie = PackVeggie(
        veg_name='Carrot',
        pack_quantity=1.5,
        price_per_pack=2.0
    )
    test_db.add(new_pack_veggie)
    test_db.commit()
    return new_pack_veggie

def test_pack_veggie_initialization(test_db):
    # Test initializing a PackVeggie instance
    new_pack_veggie = PackVeggie(
        veg_name='Spinach',
        pack_quantity=1.0,
        price_per_pack=3.0
    )
    assert new_pack_veggie.veg_name == 'Spinach'
    assert new_pack_veggie.pack_quantity == 1.0
    assert new_pack_veggie.price_per_pack == 3.0

def test_calculate_pack_price(sample_pack_veggie):
    # Test the calculate_pack_price method
    expected_price = sample_pack_veggie.calculate_pack_price(3, sample_pack_veggie.price_per_pack)
    assert expected_price == 6.0  # 3 * 2.0 = 6.0

def test_calculate_pack_price_zero_quantity(sample_pack_veggie):
    # Test calculating price with zero quantity
    expected_price = sample_pack_veggie.calculate_pack_price(0, sample_pack_veggie.price_per_pack)
    assert expected_price == 0.0  # 0 * 2.0 = 0.0

def test_calculate_pack_price_negative_quantity(sample_pack_veggie):
    # Test calculating price with negative quantity
    expected_price = sample_pack_veggie.calculate_pack_price(-1, sample_pack_veggie.price_per_pack)
    assert expected_price == -2.0  # -1 * 2.0 = -2.0