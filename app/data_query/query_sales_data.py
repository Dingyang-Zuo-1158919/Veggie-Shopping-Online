from datetime import datetime, timedelta
from app import db_session
from models.item import Item
from models.order import Order
from models.order_line import OrderLine
from models.pack_veggie import PackVeggie
from models.payment import Payment
from models.premade_box import BoxContent, PremadeBox
from models.unit_price_veggie import UnitPriceVeggie
from models.weighted_veggie import WeightedVeggie
from sqlalchemy import  func, case

def fetch_sales_data(selected_month=None, selected_year=None):
    # Define current date
    current_date = datetime.now()

    # Calculate the start dates for the week
    current_week = current_date - timedelta(days=current_date.weekday())

    # Use the selected month and year, or default to the current month and year
    if selected_month and selected_year:
        current_month = selected_month
    else:
        current_month = current_date.month

    if selected_year:
        current_year = selected_year
    else:
        current_year = current_date.year

    # Calculate the first day of the selected month/year
    first_day_of_month = datetime(int(current_year), int(current_month), 1)

    # Calculate the first day of the next month to set the upper limit for the query
    if current_month == 12:
        first_day_of_next_month = datetime(current_year + 1, 1, 1)
    else:
        first_day_of_next_month = datetime(current_year, current_month + 1, 1)

    # Query total sales amount for current week, month and year
    weekly_sales_amount = db_session.query(func.sum(Payment.payment_amount))\
                                    .join(Order, Order.payment_id == Payment.id)\
                                    .filter(Order.order_status == 'Processed', Order.order_date >= current_week).scalar() or 0
    
    monthly_sales_amount = db_session.query(func.sum(Payment.payment_amount))\
                                     .join(Order, Order.payment_id == Payment.id)\
                                     .filter(Order.order_status == 'Processed', 
                                             Order.order_date >= first_day_of_month,
                                             Order.order_date < first_day_of_next_month).scalar() or 0
    
    annual_sales_amount = db_session.query(func.sum(Payment.payment_amount))\
                                    .join(Order, Order.payment_id == Payment.id)\
                                    .filter(Order.order_status == 'Processed', 
                                            Order.order_date >= datetime(current_year, 1, 1),
                                            Order.order_date < datetime(current_year + 1, 1, 1)).scalar() or 0
    
    # Query top 10 best-selling items including item names and types from subclasses
    top_selling_items = db_session.query(
            Item.id.label("item_id"),
            func.coalesce(
                UnitPriceVeggie.veg_name, 
                WeightedVeggie.veg_name, 
                PackVeggie.veg_name, 
                PremadeBox.box_size
            ).label("item_name"),  # Use coalesce to get the name from either class
            case(
                    (UnitPriceVeggie.id != None, "Unit Price Veggie"),  # Label the type as "Unit Price Veggie"
                    (WeightedVeggie.id != None, "Weighted Veggie"),      # Label the type as "Weighted Veggie"
                    (PackVeggie.id != None, "Pack Veggie"),              # Label the type as "Pack Veggie"
                    (PremadeBox.id != None, "Premade Box"),               # Label the type as "Premade Box"
                    else_="Other"
            ).label("item_type"),
            func.sum(OrderLine.item_number).label("total_sold")
        ).outerjoin(UnitPriceVeggie, OrderLine.an_item_id == UnitPriceVeggie.id)\
        .outerjoin(WeightedVeggie, OrderLine.an_item_id == WeightedVeggie.id)\
        .outerjoin(PackVeggie, OrderLine.an_item_id == PackVeggie.id)\
        .outerjoin(BoxContent, OrderLine.box_content_id == BoxContent.id)\
        .outerjoin(PremadeBox, BoxContent.premade_box_id == PremadeBox.id)\
        .join(Order, Order.id == OrderLine.order_id)\
        .join(Payment, Payment.id == Order.payment_id)\
        .filter(Order.order_status == 'Processed')\

    # Apply filters based on the selected month and year
    if selected_year:
        # If a year is selected, filter by the year
        top_selling_items = top_selling_items.filter(
            Order.order_date >= datetime(current_year, 1, 1),
            Order.order_date < datetime(current_year + 1, 1, 1)
        )
        
        if selected_month:
            # If a month is also selected, filter by both month and year
            top_selling_items = top_selling_items.filter(
                Order.order_date >= first_day_of_month,
                Order.order_date < first_day_of_next_month
            )

    # Group, order, and limit the results
    top_selling_items = top_selling_items.group_by(Item.id, 
                                                    UnitPriceVeggie.id, 
                                                    WeightedVeggie.id, 
                                                    PackVeggie.id, 
                                                    PremadeBox.id)\
                                          .order_by(func.sum(OrderLine.item_number).desc())\
                                          .limit(10).all()

    # Prepare a list of top-selling items
    top_items_list = [
        {
            'item_id': item.item_id,
            'item_name': item.item_name,  # Include item name
            'item_type': item.item_type,    # Include item type
            'total_sold': item.total_sold
        } for item in top_selling_items
    ]

    # Return the sales data and top items
    return {
        'weekly_sales_amount': round(weekly_sales_amount, 2),
        'current_month': datetime(current_year, current_month, 1).strftime("%B %Y"),  
        'current_year': current_year,
        'monthly_sales_amount': round(monthly_sales_amount, 2),
        'annual_sales_amount': round(annual_sales_amount, 2),
        'top_items': top_items_list
    }
