from flask import (
    Blueprint,
    Flask,
    app,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    jsonify,
    abort,
    session,
    send_file,
    make_response,
)
from . import db
from .models import (
    Admin,
    Expert,
    Task,
    Quiz,
    User,
    Startcourse,
    quiz_Result,
    Course,
    Feedback,
    Msg,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from io import BytesIO
import json
from sqlalchemy import and_
from sqlalchemy.orm import joinedload


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # print(email, password)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                # print("Logged in")
                flash("Logged in successfully", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password", category="error")
        else:
            flash("User does not exists", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists.", category="error")
        elif len(name) < 2:
            flash("name must be greater than 2 charcters", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 4 charcters", category="error")
        elif password != password2:
            flash("Password does not match", category="error")
        elif len(password) < 7:
            flash("Password must be at least 7 characters", category="error")
        else:
            new_user = User(
                name=name,
                email=email,
                number=number,
                address=address,
                pincode=pincode,
                password=generate_password_hash(password, method="sha256"),
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created", category="Success")
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))

    return render_template("signup.html", user=current_user)


@auth.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():
    # Fetch the course IDs from Startcourse for the current user
    course_ids = [
        course_id
        for (course_id,) in Startcourse.query.filter_by(userid=current_user.id)
        .with_entities(Startcourse.courseid)
        .all()
    ]

    if course_ids:
        # If course_ids exist, retrieve the expert IDs from the Expert table
        expert_ids = [
            expert.id
            for expert in Expert.query.filter(Expert.course_id.in_(course_ids)).all()
        ]

        if expert_ids:
            # If expert_ids exist, retrieve the quiz data from the Quiz table
            quizzes = (
                db.session.query(
                    Quiz.title,
                    Quiz.time_limit,
                    Quiz.status,
                    db.func.count().label("column_count"),
                    (db.func.count() * Quiz.cans).label("total_score"),
                )
                .filter(Quiz.expert_id.in_(expert_ids))
                .group_by(Quiz.title)
                .all()
            )

        else:
            quizzes = []  # No expert IDs found, so no quizzes available
    else:
        quizzes = []  # No course IDs found, so no quizzes available

    # Return the quiz data
    return render_template("assignments.html", quizzes=quizzes, user=current_user)


@auth.route("/startquiz", methods=["GET", "POST"])
@login_required
def start_quiz():
    quiz_title = request.args.get("quizTitle")
    session["quiz_title"] = quiz_title
    if request.method == "POST":
        answers = {}
        question_ids = request.form.getlist("question_ids[]")
        for question_id in question_ids:
            answer = request.form.get(question_id)
            answers[question_id] = answer
        quiz_title = request.form.get("quiz_title")

        # Store the user answers in the database or process them as needed

        # Redirect to the result page with the answer dictionary and quiz title
        return redirect(
            url_for("auth.result", quiz_title=quiz_title, answers=json.dumps(answers))
        )

    quiz = Quiz.query.filter(Quiz.title == quiz_title).all()
    interval = 30

    return render_template(
        "quiz.html",
        quiz=quiz,
        interval=interval,
        user=current_user,
        answers={},
        quiz_title=quiz_title,
    )


@auth.route("/result", methods=["GET", "POST"])
@login_required
def result():
    quiz_title = request.args.get("quiz_title")
    # session.pop("quiz_title", None)  # Corrected key
    # print(quiz_title)
    answers = json.loads(request.args.get("answers"))
    # print(answers)
    quiz = Quiz.query.filter(Quiz.title == quiz_title).all()
    correct_count = 0

    for question in quiz:
        question_id = str(question.id)
        user_answer = answers.get(question_id)

        # Compare the user's answer with the correct answer
        # print(f"Question: {question.question}")
        # print(f"User's answer: {user_answer}")
        # print(f"Correct answer: {question.ans}")

        if user_answer and user_answer == question.ans:
            correct_count += 1

    # Calculate the percentage of correct answers
    total_questions = len(quiz)
    percentage = 0
    if total_questions > 0:
        percentage = (correct_count / total_questions) * 100

    # print(correct_count)
    # print(percentage)

    result = quiz_Result(
        quiz_title=quiz_title, percentage=percentage, userid=current_user.id
    )
    # Check if the user ID already exists
    existing_result = quiz_Result.query.filter_by(userid=current_user.id).first()

    if existing_result is None:
        # User ID does not exist, proceed with adding the quiz result
        db.session.add(result)
        db.session.commit()
        flash("Response Addded Successfully", category="Success")
    else:
        flash("There is already a response", category="error")

    return render_template(
        "result.html",
        percentage=percentage,
        total_questions=total_questions,
        quiz_title=quiz_title,
        user=current_user,
    )


@auth.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    userid = current_user.id
    start_course = Startcourse.query.filter_by(userid=userid).first()
    course = None

    if start_course:
        course_id = start_course.courseid

        # Query the Course table to get the course name
        course = Course.query.get(course_id)

    results = quiz_Result.query.filter_by(userid=userid).all()
    total_percentage = sum(result.percentage for result in results)
    average_percentage = total_percentage / len(results) if len(results) > 0 else 0
    # print(average_percentage)

    return render_template(
        "Progress.html",
        course=course,
        results=results,
        average_percentage=average_percentage,
        user=current_user,
    )


@auth.route("/material", methods=["GET", "POST"])
@login_required
def material():
    # Fetch the course IDs from Startcourse for the current user
    course_ids = [
        course_id
        for (course_id,) in Startcourse.query.filter_by(userid=current_user.id)
        .with_entities(Startcourse.courseid)
        .all()
    ]

    tasks = []
    if course_ids:
        # If course_ids exist, retrieve the expert IDs from the Expert table
        expert_ids = [
            expert.id
            for expert in Expert.query.filter(Expert.course_id.in_(course_ids)).all()
        ]

        if expert_ids:
            tasks = Task.query.filter(Task.expert_id.in_(expert_ids)).all()

    return render_template("material.html", tasks=tasks, user=current_user)


@auth.route("/download/<int:task_id>", methods=["GET"])
def download_task(task_id):
    task = Task.query.get(task_id)
    if task:
        response = make_response(task.data)
        response.headers.set(
            "Content-Disposition", "attachment", filename=task.filename
        )
        return response
    else:
        flash("Task not found.", "error")
        return redirect(url_for("auth.material"))


@auth.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        feed = Feedback.query.filter_by(email=email).first()
        if feed:
            flash("You have already sended 1 feedback", category="error")

        else:
            feb = Feedback(
                name=name,
                email=email,
                subject=subject,
                message=message,
                userid=current_user.id,
            )
            db.session.add(feb)
            db.session.commit()
            flash("Feedback Send successfully", category="Success")
            return redirect(url_for("views.home"))

    return render_template("inner_Contact.html", user=current_user)


@auth.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == "POST":
        name = None
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("feedback")

        feed = Feedback.query.filter_by(email=email).first()
        if feed:
            flash("You have already sended 1 feedback", category="error")

        else:
            feb = Feedback(
                name=name,
                email=email,
                subject=subject,
                message=message,
                userid=None,
            )
            db.session.add(feb)
            db.session.commit()
            flash("Feedback Send successfully", category="Success")
            return redirect(url_for("views.index"))

    return render_template("contact_us.html", user=current_user)


@auth.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    start_course = Startcourse.query.filter_by(userid=current_user.id).first()
    expert = None

    if start_course:
        courseid = start_course.courseid
        course = Course.query.filter_by(id=courseid).first()
        if course:
            experts = (
                course.expertid
            )  # Access the experts associated with the course using the 'expertid' attribute
            if experts:
                expert = experts[0]  # Select the first expert from the list

    if request.method == "POST":
        msg = request.form.get("msg")

        if expert:
            chat = Msg(
                msg=msg,
                sender=current_user.name,
                userid=current_user.id,
                expertid=expert.id,
            )
            db.session.add(chat)
            db.session.commit()
            flash("Message Sent Successfully", category="success")
        else:
            flash("No expert found for the course", category="error")

    messages = (
        Msg.query.filter(Msg.userid == current_user.id, Msg.expertid == expert.id).all()
        if expert
        else []
    )

    return render_template(
        "chat.html", user=current_user, expert=expert, messages=messages
    )


@auth.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if email is not None:
            email = email.strip()

            if password == password2:
                user = User.query.filter_by(email=email).first()
                print(email)
                print(user)

                if user:
                    user.password = generate_password_hash(password, method="sha256")
                    db.session.commit()
                    flash("Password changed successfully", category="success")
                    return redirect(url_for("auth.login"))
                else:
                    flash("User not found", category="error")
            else:
                flash("Please enter the same password twice", category="error")
        else:
            flash("Email is missing", category="error")

    return render_template("forgot.html")
