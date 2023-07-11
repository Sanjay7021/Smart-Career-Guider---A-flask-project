from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(255))
    expertid = db.relationship("Expert", backref="course")


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))


class Expert(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    specialization = db.Column(db.String(150))
    experince = db.Column(db.Integer)
    password = db.Column(db.String(150))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Description = db.Column(db.String(100))
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    expert_id = db.Column(db.Integer, db.ForeignKey("expert.id"))


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    cans = db.Column(db.Integer)
    time_limit = db.Column(db.Integer)
    question = db.Column(db.String(255))
    op1 = db.Column(db.String(100))
    op2 = db.Column(db.String(100))
    op3 = db.Column(db.String(100))
    op4 = db.Column(db.String(100))
    ans = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=False, nullable=False)
    expert_id = db.Column(db.Integer, db.ForeignKey("expert.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    number = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(100))
    pincode = db.Column(db.String(100))
    password = db.Column(db.String(150))


class Startcourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    courseid = db.Column(db.Integer, db.ForeignKey("course.id"))


class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    overall = db.Column(db.Integer)
    expertid = db.Column(db.Integer, db.ForeignKey("expert.id"))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    subject = db.Column(db.String(150))
    message = db.Column(db.String(255))
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))


class Msg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.String(255))
    date = db.Column(db.Date, default=datetime.now().date())
    time = db.Column(db.Time, default=datetime.now().time())
    sender = db.Column(db.String(255))
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    expertid = db.Column(db.Integer, db.ForeignKey("expert.id"))
