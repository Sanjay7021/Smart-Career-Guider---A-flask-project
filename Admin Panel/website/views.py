from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import Admin, Expert, Course, User, Msg, Feedback
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    admin_name = current_user.name
    return render_template("index.html", name=admin_name, admin=current_user)


@views.route("/delete-expert", methods=["POST"])
def delete_note():
    expert = json.loads(request.data)
    expertid = expert["expertid"]
    print(expertid)
    expert = Expert.query.get(expertid)
    db.session.delete(expert)
    db.session.commit()

    return jsonify({})


@views.route("/delete-user", methods=["POST"])
def delete_user():
    user = json.loads(request.data)
    userid = user["userid"]
    print(userid)
    user = User.query.get(userid)
    db.session.delete(user)
    db.session.commit()

    return jsonify({})


@views.route("/delete-feed", methods=["POST"])
def delete_feed():
    feed = json.loads(request.data)
    feedid = feed["feedid"]
    print(feedid)
    feed = Feedback.query.get(feedid)
    db.session.delete(feed)
    db.session.commit()

    return jsonify({})


@views.route("/delete-chat", methods=["POST"])
def delete_chat():
    chat = json.loads(request.data)
    chatid = chat["chatid"]
    print(chatid)
    chat = Msg.query.get(chatid)
    db.session.delete(chat)
    db.session.commit()

    return jsonify({})


@views.route("/delete-course", methods=["POST"])
def delete_course():
    course = json.loads(request.data)
    courseid = course["courseid"]
    print(courseid)
    course = Course.query.get(courseid)
    db.session.delete(course)
    db.session.commit()

    return jsonify({})
