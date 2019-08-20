
"""
Resets the db and populates with data dir rows
"""
from app.startup import app, db, init_app
from app.models import *
import numpy, pickle
from random import shuffle

"""
Delete all tables, then create all tables
"""
def reset_db(db):
    # TODO: query everything and save in some (sql and/or csv) file
    
    # Drop all tables
    print("Dropping all tables")
    # Enables cascade (children before parents)
    db.reflect()
    db.drop_all()

    # Create all tables
    print("Creating all tables")
    db.create_all()

    return

"""
Inserting data dirs
"""
def populate_db(db):
    print("Populating db with data dirs")
    
    dropped = [55, 57, 75, 97]
    for name in range(100):
        if name not in dropped:
            item = DataDir(name=name)
            db.session.add(item)
            db.session.commit()

    test = DataDir.query.all()
    print('DataDir 4')
    print(test[4])

    return

# Initialize the app, reset the database, test 
if __name__ == "__main__":
    init_app(app, db)
    reset_db(db)
    populate_db(db)
