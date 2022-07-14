from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    checklist = db.relationship("ChecklistEntry", lazy='dynamic')
    extras = db.relationship("UserExtras", uselist=False)

    def get_status(self, pid):
        return self.checklist.filter_by(pid=pid).first()


class UserExtras(db.Model):
    id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    unique_key = db.Column(db.String(150))
    diff_pref = db.Column(db.Integer)


class ChecklistEntry(db.Model):
    user_id = db.Column(db.ForeignKey("user.id"), primary_key=True)
    pid = db.Column(db.ForeignKey("problem.id"), primary_key=True)
    date = db.Column(db.DateTime)
    progress = db.Column(db.String(10))

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    year = db.Column(db.Integer)
    month = db.Column(db.String(10))
    div = db.Column(db.String(10))
    name = db.Column(db.String(50))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
