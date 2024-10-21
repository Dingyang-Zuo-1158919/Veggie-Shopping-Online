import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')

app.secret_key = 'final_pj_session_key'

app.config['SECRET_KEY'] = 'final_project_secret_key'
app.config['UPLOAD_FOLDER'] = 'app/static/project_images'
bcrypt = Bcrypt(app)

# SQLAlchemy setup
engine = create_engine('mysql+mysqlconnector://root:ZDYzdy123@localhost/final_pj')
Session = sessionmaker(bind=engine)
db_session = Session()

# Import all models to ensure they are registered
import models.person
import models.staff
import models.customer
import models.corporate_customer
import models.payment
import models.credit_card_payment
import models.debit_card_payment
import models.order
import models.order_line
import models.item
import models.veggie
import models.premade_box
import models.weighted_veggie
import models.unit_price_veggie

# Create the tables
from models.database import Base 
Base.metadata.create_all(engine)

# Configure ProxyFix if running on PythonAnywhere
if os.environ.get('PYTHONANYWHERE_SITE'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Import routes after initializing the app to avoid circular imports
from app.controllers import * 

# Set error redirect page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html'), 500
