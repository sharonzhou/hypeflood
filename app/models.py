from app import db
import datetime

class Worker(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amt_id = db.Column(db.String())

    def __repr__(self):
        return "<Worker {}. AMT id {}.>".format(self.id, self.amt_id)

class Triplet(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    root_img = db.Column(db.Integer(), default=-1)
    img1 = db.Column(db.Integer(), default=-1)
    img2 = db.Column(db.Integer(), default=-1)
    img_selected = db.Column(db.Integer(), default=-1)

    uid = db.Column(db.Integer(), db.ForeignKey(Worker.id))

    def __repr__(self):
        return "<Triplet {}, selected {} out of root {} and img1 {} img2 {}. UID {}>".format(self.id, self.img_selected, self.root_img, self.img1, self.img2, self.uid)


db.create_all()
