
"""
Runs the server, calling the Flask app and db to initialize.
"""
from app.startup import app, db, init_app

init_app(app, db)

if __name__ == "__main__":
    app.run(debug=True)
