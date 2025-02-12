from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SECRET_KEY'] = '12345' 
db = SQLAlchemy(app)

import secrets

secret_key = secrets.token_hex(16)  # Generate a 16-byte random key
print(secret_key)

from app.routes import *