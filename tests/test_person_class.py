import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models.person import Person
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


def test_person_creation(test_db):
    # Test creating a new Person
    new_person = Person(first_name='John', last_name='Doe', password='securepassword', username='johndoe')
    test_db.add(new_person)
    test_db.commit()

    # Retrieve the person from the database
    retrieved_person = test_db.query(Person).filter_by(username='johndoe').first()

    assert retrieved_person is not None
    assert retrieved_person.first_name == 'John'
    assert retrieved_person.last_name == 'Doe'
    assert retrieved_person.username == 'johndoe'


def test_username_uniqueness(test_db):
    # Create a first person
    person1 = Person(first_name='Alice', last_name='Smith', password='password1', username='alice')
    test_db.add(person1)
    test_db.commit()

    # Try to create a second person with the same username
    person2 = Person(first_name='Bob', last_name='Jones', password='password2', username='alice')

    with pytest.raises(IntegrityError):
        test_db.add(person2)
        test_db.commit()

    # Rollback the session after exception
    test_db.rollback()


def test_missing_fields(test_db):
    # Test creating a Person without required fields
    incomplete_person = Person(first_name='Charlie', last_name='Brown', password='')

    with pytest.raises(Exception):  
        test_db.add(incomplete_person)
        test_db.commit()
