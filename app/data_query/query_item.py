from app import db_session
from models.pack_veggie import PackVeggie
from models.premade_box import PremadeBox
from models.unit_price_veggie import UnitPriceVeggie
from models.veggie import Veggie
from models.weighted_veggie import WeightedVeggie
from sqlalchemy import  func
from sqlalchemy.orm import aliased

def paginate(items, page, items_per_page):
    total_items = len(items)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Calculate the start and end indices for slicing the list
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    
    # Get the items for the current page
    paginated_items = items[start_index:end_index]

    return paginated_items, total_items, total_pages

def fetch_all_veggies(user_type):
    # Create aliases for each table to avoid ambiguity
    WeightedVeggieAlias = aliased(WeightedVeggie)
    UnitPriceVeggieAlias = aliased(UnitPriceVeggie)
    PackVeggieAlias = aliased(PackVeggie)

    if user_type != 'staff' :
        # Query to fetch all available veggies along with their associated weights, unit prices, and pack quantities
        all_veggies = (
            db_session.query(
            Veggie.veg_name,
            func.MAX(WeightedVeggieAlias.weight).label('weight_qty'),
            func.MAX(UnitPriceVeggieAlias.quantity).label('unit_qty'),
            func.MAX(PackVeggieAlias.pack_quantity).label('pack_qty')
        )
        .select_from(Veggie)
        .outerjoin(WeightedVeggieAlias, WeightedVeggieAlias.id == Veggie.id)
        .outerjoin(UnitPriceVeggieAlias, UnitPriceVeggieAlias.id == Veggie.id)
        .outerjoin(PackVeggieAlias, PackVeggieAlias.id == Veggie.id)
        .group_by(Veggie.veg_name)
        .having(
            (func.MAX(WeightedVeggieAlias.weight) >= 1) | 
            (func.MAX(UnitPriceVeggieAlias.quantity) >= 1) | 
            (func.MAX(PackVeggieAlias.pack_quantity) >= 1)
        )
        .all()
        )
    else:
        # Staff can view all available veggies, including those with zero stock
        # Query to fetch all veggies along with their associated weights, unit prices, and pack quantities
        all_veggies = (
            db_session.query(
            Veggie.veg_name,
            func.MAX(WeightedVeggieAlias.weight).label('weight_qty'),
            func.MAX(UnitPriceVeggieAlias.quantity).label('unit_qty'),
            func.MAX(PackVeggieAlias.pack_quantity).label('pack_qty')
        )
        .select_from(Veggie)
        .outerjoin(WeightedVeggieAlias, WeightedVeggieAlias.id == Veggie.id)
        .outerjoin(UnitPriceVeggieAlias, UnitPriceVeggieAlias.id == Veggie.id)
        .outerjoin(PackVeggieAlias, PackVeggieAlias.id == Veggie.id)
        .group_by(Veggie.veg_name)
        .all()
        )

    return all_veggies
    
def fetch_all_premade_boxes(user_type):
    # Query to fetch premade box stock quantities
    premade_box_stock = (
        db_session.query(
            PremadeBox.box_size,
            PremadeBox.num_of_boxes
        ).all()
    )

    # If user_type is not 'staff', filter for boxes with num_of_boxes not equal to 0
    if user_type != 'staff':
        premade_box_stock = [
            (box_size, num_of_boxes) for box_size, num_of_boxes in premade_box_stock if num_of_boxes > 0
        ]

    return premade_box_stock