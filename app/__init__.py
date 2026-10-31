import os
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
# Set SECRET_KEY in the environment. Without it a random key is used, so sessions reset on every restart.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
db = SQLAlchemy(app)

from app.routes import *
