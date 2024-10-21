import pytest

# Mock dependencies for the POST request test cases
@pytest.fixture
def mock_dependencies(mocker):
    mock_order = mocker.patch('app.data_query.query_order')
    mock_payment = mocker.patch('app.data_query.query_payment')
    return {
        'update_stock_quantity': mock_order.update_stock_quantity,
        'get_customer_and_apply_discount': mock_order.get_customer_and_apply_discount,
        'create_order': mock_order.create_order,
        'add_order_lines': mock_order.add_order_lines,
        'process_card_payment': mock_payment.process_card_payment,
        'process_account_payment': mock_payment.process_account_payment
    }


# Test case for GET method
def test_checkout_get(client):
    with client.session_transaction() as sess:
        sess['user_type'] = 'individual_customer'
        sess['order'] = [{'item_name': 'Carrot', 'quantity': 2}]

    response = client.get('/checkout?total_order_price=100.0')

    # Check if the response renders the template with the expected data
    assert response.status_code == 200
    assert b'Checkout' in response.data  # the HTML contains 'Checkout'
    assert b'Carrot' in response.data  # Item in the order should be displayed


# Test case for POST method with missing payment method
def test_checkout_post_missing_payment_method(client):
    with client.session_transaction() as sess:
        sess['user_type'] = 'individual_customer'
        sess['order'] = [{'item_name': 'Carrot', 'quantity': 2, 'purchase_type':'weight', 'product_id':20}]

    response = client.post('/checkout', data={
        'total_order_price': 100.0,
        'total_quantity': 2
    })

    # Should redirect back to checkout with a flash message
    assert response.status_code == 400
    assert b'400 Bad Request' in response.data


# Test case for POST method with stock check failure
def test_checkout_post_insufficient_stock(client, mock_dependencies):
    mock_dependencies['update_stock_quantity'].return_value = False

    with client.session_transaction() as sess:
        sess['user_type'] = 'individual_customer'
        sess['order'] = [{'item_name': 'Carrot', 'quantity': 2, 'purchase_type':'weight', 'product_id':20}]

    response = client.post('/checkout', data={
        'payment_method': 'credit_card',
        'total_order_price': 100.0,
        'total_quantity': 2
    })

    # Should redirect to the home page due to stock failure
    assert response.status_code == 302
    assert '/' in response.headers['Location']


# Test case for POST method with valid payment and successful checkout
def test_checkout_post_successful_payment(client, mock_dependencies):
    mock_dependencies['update_stock_quantity'].return_value = True
    mock_dependencies['get_customer_and_apply_discount'].return_value = ('Customer', 90.0)

    with client.session_transaction() as sess:
        sess['user_type'] = 'corporate_customer'
        sess['user_id'] = 1
        sess['order'] = [{'item_name': 'Carrot', 'quantity': 2, 'purchase_type':'weight', 'product_id':20}]

    response = client.post('/checkout', data={
        'payment_method': 'credit_card',
        'total_order_price': 100.0,
        'total_quantity': 2
    })

    # Ensure successful redirection and flash message
    assert response.status_code == 302
    assert '/' in response.headers['Location']


# Test case for POST method with invalid user type
def test_checkout_post_invalid_user_type(client, mock_dependencies):
    mock_dependencies['get_customer_and_apply_discount'].return_value = (None, 0)

    with client.session_transaction() as sess:
        sess['user_type'] = 'invalid_type'
        sess['user_id'] = 1
        sess['order'] = [{'item_name': 'Carrot', 'quantity': 2, 'purchase_type':'weight', 'product_id':20}]

    response = client.post('/checkout', data={
        'payment_method': 'account',
        'total_order_price': 100.0,
        'total_quantity': 2
    })

    # Should redirect to checkout with invalid user type flash message
    assert response.status_code == 302
    assert '/' in response.headers['Location']

