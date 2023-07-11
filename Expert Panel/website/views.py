from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from . import db
import json
from .models import Quiz

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    expert_name = current_user.name
    return render_template("index.html", name=expert_name, expert=current_user)


@views.route("/delete-quiz", methods=["POST"])
def delete_quiz():
    quiz_data = json.loads(request.data)
    title = quiz_data["title"]

    quiz = Quiz.query.filter_by(title=title).first()
    if quiz:
        quiz_id = quiz.id  # Assuming 'id' is the primary key column name
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"message": f"Quiz with ID {quiz_id} deleted successfully"})
    else:
        return jsonify({"error": "Quiz not found"})


@views.route("/active-quiz", methods=["POST"])
def active_quiz():
    quiz_data = json.loads(request.data)
    title = quiz_data["title"]

    quiz = Quiz.query.filter_by(title=title).all()
    if quiz:
        for q in quiz:
            q.status = not q.status
        db.session.commit()
        return jsonify({"message": f"Quiz with ID {quiz.id} updated successfully"})
    else:
        return jsonify({"error": "Quiz not found"})
