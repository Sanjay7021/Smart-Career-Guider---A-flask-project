from flask import (
    Blueprint,
    app,
    render_template,
    flash,
    request,
    jsonify,
    redirect,
    url_for,
)
from sqlalchemy.orm.exc import NoResultFound
from flask_login import login_user, login_required, logout_user, current_user
from . import db
import json
from .models import Quiz, Course, Startcourse, User
from sqlalchemy import and_

views = Blueprint("views", __name__)


@views.before_request
def prevent_cache():
    if request.endpoint in ["logout", "home"]:
        # Add additional pages that should not be cached as needed
        response = app.make_response()
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


@views.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", user=current_user)


@views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    username = current_user.name
    # Fetch only the courseid from Startcourse for the current user
    course_ids = [
        course_id
        for (course_id,) in Startcourse.query.filter_by(userid=current_user.id)
        .with_entities(Startcourse.courseid)
        .all()
    ]

    if course_ids:
        # If course_ids exist, retrieve the corresponding course data
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
    else:
        # If course_ids do not exist, retrieve all course data
        courses = Course.query.all()

    # Return the course data
    return render_template(
        "home.html", username=username, courses=courses, user=current_user
    )


@views.route("/joincourse", methods=["POST"])
@login_required
def join_course():
    join_course = json.loads(request.data)
    courseid = join_course["courseid"]

    existing_start = Startcourse.query.filter_by(
        userid=current_user.id, courseid=courseid
    ).first()

    if existing_start is None:
        # User ID does not exist, proceed with adding the start record
        start = Startcourse(userid=current_user.id, courseid=courseid)
        db.session.add(start)
        db.session.commit()
    else:
        flash("You have already choosen subject", "error")

    return jsonify({})


@views.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        address = request.form.get("address")
        pincode = request.form.get("pincode")

        try:
            # Retrieve the current user from the database
            user = User.query.filter_by(id=current_user.id).one()

            # Update the user's information
            user.name = name
            user.email = email
            user.number = number
            user.address = address
            user.pincode = pincode

            # Commit the changes to the database
            db.session.commit()
            flash("Account Updated Successfully", "Success")
            # Optionally, you can redirect the user to a success page
            return redirect(url_for("views.home"))

        except NoResultFound:
            # Handle the case where the user is not found in the database
            flash("User not found.")
            return redirect(url_for("sign_up"))

    return render_template("/account.html", user=current_user)
