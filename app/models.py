from app import db
import datetime

class Worker(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amt_id = db.Column(db.String())

    def __repr__(self):
        return "<Worker {}. AMT id {}.>".format(self.id, self.amt_id)

class Selection(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    img_id = db.Column(db.Integer(), default=-1)
    img_src = db.Column(db.Integer(), default=-1)
    
    selected = db.Column(db.String())

    uid = db.Column(db.Integer(), db.ForeignKey(Worker.id))

    def __repr__(self):
        return "<Selection {}, selected {} for image {}, by worker {}>".format(self.id, self.selected, self.img_id, self.uid)


db.create_all()
