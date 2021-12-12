import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Flask Object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'MY SECRET KEY'
app.config['DEBUG'] = False

# Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/ProjectQR"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Saving photo configuration
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(APP_ROOT, 'static/scannedqr/')

# Database Representation
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure Flask Login
login = LoginManager(app)
login.init_app(app)
login.session_protection = "strong"


@login.user_loader
def load_user(userid):
    return models.Users.query.get(int(userid))


from app import models, routes
