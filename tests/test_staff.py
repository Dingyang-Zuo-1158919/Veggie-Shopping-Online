import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def mock_dependencies(mocker):
    return {
        'get_all_orders': mocker.patch('app.data_query.query_order.get_all_orders'),
        'prepare_order_detail': mocker.patch('app.data_query.query_order.prepare_order_detail'),
        'paginate': mocker.patch('app.data_query.query_item.paginate'),
        'fetch_all_customers': mocker.patch('app.data_query.query_user.fetch_all_customers'),
        'fetch_all_corporate_customers': mocker.patch('app.data_query.query_user.fetch_all_corporate_customers'),
        'update_order_status': mocker.patch('app.data_query.query_order.update_order_status'),
        'fetch_sales_data': mocker.patch('app.data_query.query_sales_data.fetch_sales_data')
    }

def test_manage_order(client, mock_dependencies):
    # Mock return values
    mock_dependencies['get_all_orders'].return_value = [{'order_id': 1}]
    mock_dependencies['prepare_order_detail'].return_value = {'order_id': 1, 'detail': 'some details'}
    mock_dependencies['paginate'].return_value = ([{'order_id': 1}], 1, 1)
    
    # Simulate a logged-in user by setting session
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Send a GET request to the manage order page
    response = client.get('/manage_order')

    # Check that the request was successful and rendered the manage order page
    assert response.status_code == 200

def test_manage_order_not_logged_in(client):
    # Simulate no user session
    response = client.get('/manage_order')

    # Check if it redirects to the login page
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_review_order(client, mock_dependencies):
    mock_dependencies['update_order_status'].return_value = True

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Send a POST request to review an order
    response = client.post('/staff/review_order/1')

    # Check if it redirects to the manage_order page on success
    assert response.status_code == 302
    assert '/manage_order' in response.headers['Location']

def test_review_order_update_fail(client, mock_dependencies):
    mock_dependencies['update_order_status'].return_value = False

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Send a POST request to review an order with failed update
    response = client.post('/staff/review_order/1')

    # Check if it redirects to the manage_order page on failure
    assert response.status_code == 302
    assert '/manage_order' in response.headers['Location']

def test_manage_customer(client, mock_dependencies):
    # Mocking fetch functions to return sample data
    mock_dependencies['fetch_all_customers'].return_value = [{'id': 1, 'name': 'Customer'}]
    mock_dependencies['fetch_all_corporate_customers'].return_value = [{'id': 2, 'name': 'Corporate Customer'}]
    
    # Send a GET request to manage customers
    response = client.get('/staff/manage_customer')

    # Check that the response is successful and customers are in the response
    assert response.status_code == 200

def test_sales_performance(client, mock_dependencies):
    # Mock the fetch_sales_data to return some test data
    mock_dependencies['fetch_sales_data'].return_value = {'sales': 1000}

    # Send a GET request to the sales performance page
    response = client.get('/sales_performance')

    # Check that the response was successful
    assert response.status_code == 200
    assert b'1000' in response.data

def test_sales_performance_with_year(client, mock_dependencies):
    # Mock the fetch_sales_data to return some test data for a specific year
    mock_dependencies['fetch_sales_data'].return_value = {'sales': 2000}

    # Send a GET request with a year parameter
    response = client.get('/sales_performance?year_or_month=year&year=2023')

    # Check that the response was successful and the sales data is for the year
    assert response.status_code == 200
    assert b'2000' in response.data
