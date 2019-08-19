
"""
Startup script called by runserver.py for running the Flask application, initializing app and db.
The instances of app and db live here and must be imported by other files.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from app import app

app.config['SECRET_KEY']=secrets.token_urlsafe(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)

def init_app(app, db):
    from app import models
    from app import views
    db.create_all()
    return app
