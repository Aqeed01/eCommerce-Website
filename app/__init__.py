import os
import secrets
import shutil

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

HERE = os.path.dirname(os.path.abspath(__file__))


def database_uri():
    """SQLite file next to the app. On Vercel the code is read-only, so the bundled demo
    database is copied to /tmp on first use; changes there reset when the instance restarts."""
    if os.environ.get("VERCEL"):
        target = os.path.join("/tmp", "ecommerce.db")
        if not os.path.exists(target):
            shutil.copy(os.path.join(os.path.dirname(HERE), "instance", "ecommerce.db"), target)
        return "sqlite:///" + target
    return "sqlite:///ecommerce.db"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri()
# Set SECRET_KEY in the environment. Without it a random key is used, so sessions reset on every restart.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = bool(os.environ.get('VERCEL'))
db = SQLAlchemy(app)

from app.routes import *
