
"""
Runs the server, calling the Flask app and db to initialize.
"""
from app.startup import app, db, init_app
import secrets
import os

app.config['SECRET_KEY']=secrets.token_urlsafe(16)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

init_app(app, db)

if __name__ == "__main__":
    app.run(debug=True)
