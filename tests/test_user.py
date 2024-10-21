import pytest
from app import app  # Import your Flask app
from app.data_query.query_user import get_customer_by_id, get_corporate_customer_by_id, get_staff_by_id

# Fixture for setting up the Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Mocking the data_query functions
def mock_get_customer_by_id(user_id):
    return {'id': user_id, 'name': 'John Doe'}

def mock_get_corporate_customer_by_id(user_id):
    return {'id': user_id, 'name': 'Acme Corp'}

def mock_get_staff_by_id(user_id):
    return {'id': user_id, 'name': 'Jane Smith'}

@pytest.fixture(autouse=True)
def mock_queries(monkeypatch):
    monkeypatch.setattr('app.data_query.query_user.get_customer_by_id', mock_get_customer_by_id)
    monkeypatch.setattr('app.data_query.query_user.get_corporate_customer_by_id', mock_get_corporate_customer_by_id)
    monkeypatch.setattr('app.data_query.query_user.get_staff_by_id', mock_get_staff_by_id)

def test_user_profile_valid_customer(client):
    response = client.get('/user_profile/1/customer')
    assert response.status_code == 302

def test_user_profile_valid_corporate_customer(client):
    response = client.get('/user_profile/1/corporate_customer')
    assert response.status_code == 302
    
def test_user_profile_valid_staff(client):
    response = client.get('/user_profile/1/staff')
    assert response.status_code == 302
    
def test_user_profile_invalid_user_type(client):
    response = client.get('/user_profile/1/invalid_type')
    assert response.status_code == 302  # Expecting a redirect

def test_user_profile_user_not_found(client, monkeypatch):
    # Mocking a function to return None (user not found)
    def mock_get_customer_by_id_not_found(user_id):
        return None
    
    monkeypatch.setattr('app.data_query.query_user.get_customer_by_id', mock_get_customer_by_id_not_found)

    response = client.get('/user_profile/1/customer')
    assert response.status_code == 302  # Expecting a redirect

def test_user_profile_exception_handling(client, monkeypatch):
    # Mocking a function to raise an exception
    def mock_get_customer_by_id_exception(user_id):
        raise Exception("Database error")
    
    monkeypatch.setattr('app.data_query.query_user.get_customer_by_id', mock_get_customer_by_id_exception)

    response = client.get('/user_profile/1/customer')
    assert response.status_code == 302  # Expecting a redirect