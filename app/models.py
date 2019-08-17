from app import db
import datetime

class Worker(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amt_id = db.Column(db.String())
    
    data_dir_id = db.Column(db.Integer())
    passed_tutorial = db.Column(db.Integer(), default=-1)

    def __repr__(self):
        return "<Worker {}. AMT id {}. data dir {}. Passed tutorial? {}.>".format(self.id, self.amt_id, self.data_dir_id, self.passed_tutorial)

class Selection(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    img_name = db.Column(db.String())
    img_src = db.Column(db.String())
    
    selected = db.Column(db.String())
    correctness = db.Column(db.Boolean())

    uid = db.Column(db.Integer(), db.ForeignKey(Worker.id))

    def __repr__(self):
        return "<Selection {}, selected {} for image {} from src {}, by worker {}>".format(self.id, self.selected, self.img_name, self.img_src, self.uid)


db.create_all()
