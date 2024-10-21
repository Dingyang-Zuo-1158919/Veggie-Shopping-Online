import pytest

@pytest.fixture
def setup_database():
    # Mock database setup
    return {
        'user_id': 1,
        'username': 'testuser',
        'password': 'testpassword',
        'order_id': 123
    }

@pytest.fixture
def setup_session(client, setup_database):
    with client.session_transaction() as sess:
        sess['user_id'] = setup_database['user_id']
    return client

def test_add_to_order_success(client):
    response = client.post('/add_to_order', data={
        'item_name': 'Carrot',
        'quantity': 3,
        'purchase_type': 'medium',
        'veggies[]': ['Lettuce', 'Spinach']
    })
    assert response.status_code == 302

def test_add_to_order_missing_fields(client):
    response = client.post('/add_to_order', data={
        'item_name': '',
        'quantity': 2,
        'purchase_type': 'medium'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] == False

def test_remove_from_order_success(setup_session):
    # Mock session with an order
    with setup_session.session_transaction() as sess:
        sess['order'] = [{'item_id': 1, 'total_price': 10}]
    
    response = setup_session.post('/remove_from_order', data={
        'item_id': 1
    })
    
    assert response.status_code == 200
    assert response.get_json()['success'] == True
    assert response.get_json()['total_order_price'] == 0

def test_remove_from_order_missing_item_id(setup_session):
    response = setup_session.post('/remove_from_order', data={})
    assert response.status_code == 400
    assert response.get_json()['success'] == False
    assert response.get_json()['message'] == 'Item ID is missing.'

def test_update_order_quantity_success(setup_session):
    with setup_session.session_transaction() as sess:
        sess['order'] = [{'item_id': 1, 'quantity': 2, 'total_price': 20}]
    
    response = setup_session.post('/update_order_quantity', data={
        'item_id': 1,
        'quantity': 3
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] == True
    assert json_data['total_order_price'] == 30  # 3 units, $10 per unit
    assert json_data['total_price'] == 30  # Updated item price

def test_update_order_quantity_invalid_input(setup_session):
    response = setup_session.post('/update_order_quantity', data={
        'item_id': '',
        'quantity': 0
    })
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['success'] == False
    assert json_data['message'] == 'Invalid item ID or quantity.'

def test_order_list_success(setup_session, mocker):
    # Mock database call
    mocker.patch('app.data_query.query_order.get_customer_orders', return_value=[
        {'order_id': 1, 'total_price': 100, 'status': 'Pending'}
    ])
    mocker.patch('app.data_query.query_order.prepare_order_detail', return_value={
        'order_id': 1, 'total_price': 100, 'status': 'Pending'
    })

    response = setup_session.get('/order_list')
    assert response.status_code == 200
    assert b'Order List' in response.data  # Assuming this string appears on the order list page

def test_order_list_not_logged_in(client):
    response = client.get('/order_list')
    assert response.status_code == 302  # Should redirect to login
    assert response.location.endswith('/login')

def test_cancel_order_success(setup_session, mocker):
    # Mock the cancel_selected_order function
    mocker.patch('app.data_query.query_order.cancel_selected_order', return_value=True)

    response = setup_session.post('/cancel_order/1', data={
        'target': '/order_list'
    })

    assert response.status_code == 302  # Redirection
    assert response.location.endswith('/order_list')

def test_cancel_order_failure(setup_session, mocker):
    mocker.patch('app.data_query.query_order.cancel_selected_order', return_value=False)

    response = setup_session.post('/cancel_order/1', data={
        'target': '/order_list'
    })

    assert response.status_code == 302  # Should still redirect but with failure message
    assert response.location.endswith('/order_list')
