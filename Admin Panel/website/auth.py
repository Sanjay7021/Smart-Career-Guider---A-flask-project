from flask import Blueprint, render_template, request, flash, url_for, redirect
from . import db
from .models import Admin, Expert, Course, User, Performance, Msg, Feedback
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from io import BytesIO

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = Admin.query.filter_by(email=email).first()
        if admin:
            if admin.password == password:
                flash("Logged in successfully", category="success")
                login_user(admin, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password", category="error")
        else:
            flash("User does not exists", category="error")

    return render_template("login.html", admin=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/Add_expert", methods=["GET", "POST"])
@login_required
def Add_expert():
    course = Course.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        specialization = request.form.get("specialization")
        experince = request.form.get("experience")
        password = request.form.get("password")
        course_id, course_name = specialization.split(":", 1)

        new_expert = Expert(
            name=name,
            email=email,
            specialization=course_name,
            experince=experince,
            password=generate_password_hash(password, method="sha256"),
            course_id=course_id,
        )
        db.session.add(new_expert)
        db.session.commit()
        flash("Expert Added successfully", category="Success")

        return redirect(url_for("views.home"))

    return render_template("Add_expert.html", admin=current_user, courses=course)


@auth.route("/expert_manage")
@login_required
def expert_manage():
    expert = Expert.query.all()
    return render_template("expert_manage.html", admin=current_user, experts=expert)


@auth.route("/student_manage")
@login_required
def student_manage():
    user = User.query.all()
    return render_template("student_manage.html", admin=current_user, users=user)


@auth.route("/message")
@login_required
def message():
    chat = Msg.query.all()
    return render_template("messages.html", chat=chat, admin=current_user)


@auth.route("/feedback")
@login_required
def feedback():
    feed = Feedback.query.all()
    return render_template("feedback.html", ouruser=feed, admin=current_user)


@auth.route("/manage_course")
@login_required
def manage_course():
    course = Course.query.all()
    return render_template("course.html", course=course, admin=current_user)


@auth.route("/Add_course", methods=["GET", "POST"])
@login_required
def Add_course():
    if request.method == "POST":
        cname = request.form.get("c_name")
        description = request.form.get("description")

        new_course = Course(name=cname, description=description)
        db.session.add(new_course)
        db.session.commit()
        flash("Course Added successfully", category="Success")

    return render_template("Add_course.html", admin=current_user)


@auth.route("/progress", methods=["GET", "POST"])
@login_required
def Progress():
    results = Performance.query.all()

    expert_ids = [result.expertid for result in results]
    performances = [result.overall for result in results]

    return render_template(
        "progress.html",
        admin=current_user,
        expert_ids=expert_ids,
        performances=performances,
    )
