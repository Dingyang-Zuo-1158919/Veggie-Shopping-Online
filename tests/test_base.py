import pytest
from werkzeug.security import generate_password_hash

@pytest.fixture
def setup_database():
    # This fixture set up a test database and populate it with test data
    return {
        "username": "testuser",
        "password": generate_password_hash("testpassword"),
        "id": 1
    }

def test_home(client, setup_database):
    # Simulate a user logged in
    with client.session_transaction() as sess:
        sess['user_id'] = setup_database['id']
        sess['user_type'] = 'customer'
    
    response = client.get('/')
    assert response.status_code == 200
    assert b'<h1>Welcome to Fresh Harvest Veggies</h1>' in response.data  # Ensure the home page template is rendered

def test_login_success(client, setup_database):
    response = client.post('/login', data={
        'username': setup_database['username'],
        'password': 'testpassword'
    })
    assert response.status_code == 200  # successful login

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Should render login.html again
    assert b'Invalid username or password' in response.data  # Check for flash message

def test_login_missing_fields(client):
    response = client.post('/login', data={
        'username': '',
        'password': ''
    })
    assert response.status_code == 200  # Should render login.html again
    assert b'Username and password are required.' in response.data  # Check for flash message

def test_logout(client, setup_database):
    with client.session_transaction() as sess:
        sess['user_id'] = setup_database['id']
        sess['username'] = setup_database['username']
        sess['user_type'] = 'customer'

    response = client.get('/logout')
    assert response.status_code == 302  # Redirect after logout

    # Check that the session is cleared
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'username' not in sess
        assert 'user_type' not in sess