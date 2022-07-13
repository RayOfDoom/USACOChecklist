from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    checklist = db.relationship("ChecklistEntry", lazy='dynamic')

    def get_problems(self, year, month, div):
        return Problem.query.filter_by(year=year, month=month, div=div).all()

    def get_status(self, pid):
        return self.checklist.filter_by(pid=pid).first()


class ChecklistEntry(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    pid = db.Column(db.ForeignKey("problem.id"), primary_key=True)
    date = db.Column(db.DateTime)
    progress = db.Column(db.String(10))


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.String(10))
    div = db.Column(db.String(10))
    name = db.Column(db.String(50))

    def get_link(self):
        return 'http://www.usaco.org/index.php?page=viewproblem2&cpid=' + str(self.pid)
