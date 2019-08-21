
"""
Resets the db and populates with data dir rows
"""
from app.startup import app, db, init_app
from app.models import *
import numpy, pickle
from random import shuffle

"""
Inserting data dirs (append without resetting)
"""
def populate_db(db):
    print("Populating db with data dirs")
    
    for name in range(100):
        item = DataDir(name=name)
        db.session.add(item)
        db.session.commit()

    test = DataDir.query.filter(DataDir.status == 'unassigned').all()
    print('DataDir 4')
    print(test[4])

    return

# Initialize the app, reset the database, test 
if __name__ == "__main__":
    init_app(app, db)
    populate_db(db)
