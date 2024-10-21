from datetime import datetime
from app.data_query.query_user import get_customer_name, get_customer_type, get_customer_user_name
from flask import redirect, url_for, session, flash
from app import db_session
from models.corporate_customer import CorporateCustomer
from models.customer import Customer
from models.order import Order
from models.order_line import OrderLine
from models.pack_veggie import PackVeggie
from models.premade_box import BoxContent, PremadeBox
from models.unit_price_veggie import UnitPriceVeggie
from models.weighted_veggie import WeightedVeggie
from sqlalchemy.orm import joinedload

def calculate_total_order_price(order):
    # Calculate the total order price from the order session
    return sum(item['total_price'] for item in order)

def update_stock_quantity():
    # Set a flag
    success = True
    order = session.get('order',[])

    for item in order:
        if item['purchase_type'] == 'weight':
            # Fetch the weighted veggie and update stock quantity
            weight_veggie = db_session.query(WeightedVeggie).filter(WeightedVeggie.id == item['product_id']).first()
            if weight_veggie and weight_veggie.weight >= item['quantity']:
                weight_veggie.weight -= item['quantity']
                db_session.commit()
            else:
                success = False

        elif item['purchase_type'] == 'pack':
            # Fetch the pack veggie and update stock quantity
            pack_veggie = db_session.query(PackVeggie).filter(PackVeggie.id == item['product_id']).first()
            if pack_veggie and pack_veggie.pack_quantity >= item['quantity']:
                pack_veggie.pack_quantity -= item['quantity']
                db_session.commit()
            else:
                success = False

        elif item['purchase_type'] == 'unit':
            # Fetch the unit veggie and update stock quantity
            unit_price_veggie = db_session.query(UnitPriceVeggie).filter(UnitPriceVeggie.id == item['product_id']).first()
            if unit_price_veggie and unit_price_veggie.quantity >= item['quantity']:
                unit_price_veggie.quantity -= item['quantity']
                db_session.commit()
            else:
                success = False

        elif item['purchase_type'] in ['small', 'medium', 'large']:
            # Fetch the premade box and update stock quantity
            box_size = item['purchase_type']
            premade_box = db_session.query(PremadeBox).filter(PremadeBox.box_size == box_size).first()
            if premade_box and premade_box.num_of_boxes >= item['quantity']:
                premade_box.num_of_boxes -= item['quantity']
                db_session.commit()
            else:
                success = False

    return success

def get_customer_orders(user_id):
    # Fetch orders for the specified customer ID
    return db_session.query(Order).options(joinedload(Order.payment)).filter(Order.customer_id == user_id).order_by(Order.order_date.desc()).all()

def get_order_by_id(order_id):
    # Fetch order by order id
    return db_session.query(Order).filter(Order.id == order_id).first()

def get_all_orders():
    # Fetch orders along with customer and payment details
    orders = (
        db_session.query(Order).options(joinedload(Order.customer), joinedload(Order.payment))  #load both customer and payment
        .order_by(Order.id.desc())
        .all()
    )

    return orders

def prepare_order_detail(order):
    # Prepare detailed order information including lines and item details
    customer_name = get_customer_name(order.customer_id)
    customer_user_name = get_customer_user_name(order.customer_id)
    customer_type = get_customer_type(order.customer_id)
    user_type = session.get('user_type')

    # Get the payment amount from the related Payment object
    payment_amount = order.payment.payment_amount if order.payment else 0.0

    order_detail = {
        'customer_name': customer_name,
        'customer_user_name': customer_user_name,
        'order_date': order.order_date,
        'order_number': order.order_number,
        'order_status': order.order_status,
        'customer_type': customer_type,
        'order_id': order.id,
        'payment_amount': payment_amount,
        'order_lines': []
    }
    
    order_lines = get_order_lines(order.id)
    for line in order_lines:
        item_detail = get_item_detail(line)
        order_detail['order_lines'].append({
            'order_line': line,
            'item_detail': item_detail
        })

    return order_detail

def get_order_lines(order_id):
    # "Fetch order lines for the specified order ID
    return db_session.query(OrderLine).filter(OrderLine.order_id == order_id).all()

def get_item_detail(line):
    # Fetch item details based on the order line
    item_detail = None

    if line.an_item_id or line.box_content_id:  # Ensure an_item_id is not None
        premade_box_content = db_session.query(BoxContent).filter(BoxContent.id == line.box_content_id).first()
        premade_box = (db_session.query(PremadeBox)
                       .filter(PremadeBox.id == premade_box_content.premade_box_id).first()
                       if premade_box_content else None)
        
        weighted_veggie = db_session.query(WeightedVeggie).filter(WeightedVeggie.id == line.an_item_id).first()
        unit_price_veggie = db_session.query(UnitPriceVeggie).filter(UnitPriceVeggie.id == line.an_item_id).first()
        pack_veggie = db_session.query(PackVeggie).filter(PackVeggie.id == line.an_item_id).first()
        
        # Determine the item type
        if premade_box:
            item_detail = {
                'type': 'PremadeBox',
                'box_content': premade_box_content.box_content,
                'box_size': premade_box.box_size,
                'quantity': line.item_number
            }
        elif weighted_veggie:
            item_detail = {
                'type': 'WeightedVeggie',
                'name': weighted_veggie.veg_name,
                'weight': weighted_veggie.weight,
                'quantity': line.item_number
            }
        elif unit_price_veggie:
            item_detail = {
                'type': 'UnitPriceVeggie',
                'name': unit_price_veggie.veg_name,
                'quantity': unit_price_veggie.quantity,
                'unit_price': unit_price_veggie.price_per_unit,
                'quantity_ordered': line.item_number
            }
        elif pack_veggie:
            item_detail = {
                'type': 'PackVeggie',
                'name': pack_veggie.veg_name,
                'pack_quantity': pack_veggie.pack_quantity,
                'quantity_ordered': line.item_number
            }
        else:
            item_detail = {
                'type': 'Unknown Item Type',
                'quantity': line.item_number
            }

    return item_detail

def initialize_order_session():
    # Initialize the order in the session if it doesn't exist
    if 'order' not in session:
        session['order'] = []

def handle_premade_box(item_name, quantity, purchase_type, selected_veggies):
    premade_box = db_session.query(PremadeBox).filter(PremadeBox.box_size == purchase_type).first()
    
    if not premade_box or premade_box.num_of_boxes < quantity:
        flash("Not enough stock available for the premade box size you select.", "danger")
        return redirect(url_for('home'))

    box_content = BoxContent(premade_box_id=premade_box.id, box_content=','.join(selected_veggies))
    db_session.add(box_content)
    db_session.commit()

    total_price = premade_box.calculate_box_price(purchase_type, quantity)
    product_id = box_content.id
    single_price = get_single_price(premade_box.box_size)

    return add_to_order_session(item_name, quantity, purchase_type, selected_veggies, total_price, product_id, float(single_price))

def handle_veggie(purchase_type, item_name, quantity):
    veggie = None
    if purchase_type == 'pack':
        veggie = db_session.query(PackVeggie).filter(PackVeggie.veg_name == item_name).first()
    elif purchase_type == 'unit':
        veggie = db_session.query(UnitPriceVeggie).filter(UnitPriceVeggie.veg_name == item_name).first()
    elif purchase_type == 'weight':
        veggie = db_session.query(WeightedVeggie).filter(WeightedVeggie.veg_name == item_name).first()

    if veggie and check_stock_availability(veggie, quantity):
        total_price, single_price = calculate_price(veggie, quantity)
        product_id = veggie.id
        return add_to_order_session(item_name, quantity, purchase_type, None, total_price, product_id, single_price)

    flash("Not enough stock available.", "danger")
    return redirect(url_for('home'))

def check_stock_availability(veggie, quantity):
    # Check stock availability for the veggie
    if isinstance(veggie, PackVeggie):
        return veggie.pack_quantity >= quantity
    elif isinstance(veggie, UnitPriceVeggie):
        return veggie.quantity >= quantity
    elif isinstance(veggie, WeightedVeggie):
        return veggie.weight >= quantity
    return False

def calculate_price(veggie, quantity):
    # Calculate price based on veggie type
    if isinstance(veggie, PackVeggie):
        return veggie.calculate_pack_price(quantity, veggie.price_per_pack), float(veggie.price_per_pack)
    elif isinstance(veggie, UnitPriceVeggie):
        return veggie.calculate_unit_price(quantity, veggie.price_per_unit), float(veggie.price_per_unit)
    elif isinstance(veggie, WeightedVeggie):
        return veggie.calculate_weight_price(quantity, veggie.weight_per_kilo), float(veggie.weight_per_kilo)

def get_single_price(box_size):
    # Get single price based on box size
    return {'small': 12, 'medium': 15, 'large': 18}.get(box_size)

def add_to_order_session(item_name, quantity, purchase_type, selected_veggies, total_price, product_id, single_price):
    # Add item to the order in session
    item_found = False
    for item in session['order']:
        if item['item_name'] == item_name and item['purchase_type'] == purchase_type and item['veggies'] == selected_veggies:
            item['quantity'] += quantity
            item['total_price'] += total_price
            item_found = True
            break

    if not item_found:
        session['order'].append({
            'item_id': len(session['order']) + 1,
            'product_id': product_id,
            'item_name': item_name,
            'quantity': quantity,
            'purchase_type': purchase_type,
            'veggies': selected_veggies,
            'total_price': float(total_price),
            'single_price': single_price
        })

    session.modified = True
    return redirect(url_for('home'))

def get_customer_and_apply_discount(user_type, user_id, total_order_price):
    # Calculate total order price by user type
    if user_type == 'corporate_customer':
        customer = db_session.query(CorporateCustomer).filter_by(id=user_id).first()
        total_order_price = float(total_order_price) * 0.9  # Apply discount
    elif user_type == 'customer':
        customer = db_session.query(Customer).filter_by(id=user_id).first()
    else:
        customer = None
    return customer, total_order_price

def create_order(user_id, total_quantity):
    new_order = Order(
        order_date=datetime.now(),
        order_number=total_quantity,
        order_status='Pending',
        customer_id=user_id
    )
    db_session.add(new_order)
    db_session.commit()
    return new_order

def add_order_lines(order_id, order_items):
    for item in order_items:
        # Determine the item type
        if item['purchase_type'] in ['small', 'medium', 'large']:
            item_type = 'Premade Box'
            order_line = OrderLine(item_number=item['quantity'],order_id=order_id, box_content_id=item['product_id'],item_type=item_type )
        elif item['purchase_type'] in ['unit', 'pack', 'weight']:
            item_type = 'Veggie'
            order_line = OrderLine(item_number=item['quantity'],order_id=order_id, an_item_id=item['product_id'],item_type=item_type )
        else:
            item_type = 'Unknown'
            order_line = OrderLine(item_number=item['quantity'],order_id=order_id, an_item_id=item['product_id'],item_type=item_type )

        db_session.add(order_line)
    db_session.commit()

def apply_discount_if_corporate(user_type, total_order_price_str):
    try:
        total_order_price = float(total_order_price_str)
        if user_type == 'corporate_customer':
            total_order_price *= 0.9
    except ValueError:
        flash('Invalid total order price format.', 'danger')
        total_order_price = 0
    return total_order_price

def update_order_status(order_id, staff_id):
    try:
        # Fetch order by id
        order = get_order_by_id(order_id)
        if not order:
            flash('Order not found.', 'danger')
            return False
        
        # Update order status
        order.order_status = 'Processed'
        order.staff_id = staff_id
        db_session.commit()

        flash(f'Order {order_id} has been marked as Processed.', 'success')
        return True
    
    except Exception as e:
        flash(f'Error updating order status: {str(e)}', 'danger')
        return False

def cancel_selected_order(order_id):
    try:
        # Fetch order by id
        order = get_order_by_id(order_id)
        if not order:
            flash('Order not found.', 'danger')
            return False

        if order and order.order_status != 'Processed':
            order.order_status = 'Cancelled'
            db_session.commit()
            flash("Order has been cancelled successfully.", "success")
            return True
        else:
            flash("Order cannot be cancelled.", "warning")
            return False
    except Exception as e:
        flash(f'Error deleting order: {str(e)}', 'danger')
        return False