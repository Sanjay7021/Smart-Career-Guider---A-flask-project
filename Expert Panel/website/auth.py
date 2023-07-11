from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    session,
    url_for,
    redirect,
    jsonify,
    abort,
)
from sqlalchemy import text
from . import db
from .models import (
    Admin,
    Expert,
    Task,
    Quiz,
    Course,
    Startcourse,
    User,
    quiz_Result,
    Performance,
    Msg,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from io import BytesIO
import json

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # print(email,password)

        expert = Expert.query.filter_by(email=email).first()
        if expert:
            if check_password_hash(expert.password, password):
                flash("Logged in successfully", category="success")
                login_user(expert, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password", category="error")
        else:
            flash("User does not exists", category="error")

    return render_template("login.html", expert=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# @auth.route("/edit_task", methods=["GET", "POST"])
# def edit_task():
#     if request.method == "POST":
#         taskdata = json.loads(request.data)
#         taskid = taskdata["taskid"]

#         task = Task.query.filter_by(id=taskid).all()
#         if not task:
#             abort(403)
#     return render_template("edit_task", task=task, expert=current_user)


@auth.route("/assign_task", methods=["GET", "POST"])
def assign_task():
    if request.method == "POST":
        description = request.form.get("description")
        file = request.files["file"]

        upload = Task(
            Description=description,
            filename=file.filename,
            data=file.read(),
            expert_id=current_user.id,
        )
        db.session.add(upload)
        db.session.commit()
        flash("File Added successfully", category="Success")
    return render_template("assign_task.html", expert=current_user)


@auth.route("/assign_quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        json_data = request.get_json()

        # Extract the values from the JSON
        quiz_data = json.loads(json_data)
        quiz_title = quiz_data[0]["title"]
        quiz_cans = quiz_data[0]["cans"]
        quiz_tl = quiz_data[0]["time_limit"]
        quiz_status = 0

        for question in quiz_data:
            quiz_question = question["question"]
            quiz_choices = question["choices"]
            quiz_answer = question["answer"]

            optiona = quiz_choices[0]
            optionb = quiz_choices[1]
            optionc = quiz_choices[2]
            optiond = quiz_choices[3]

            add_q = Quiz(
                title=quiz_title,
                cans=quiz_cans,
                time_limit=quiz_tl,
                question=quiz_question,
                op1=optiona,
                op2=optionb,
                op3=optionc,
                op4=optiond,
                ans=quiz_answer,
                status=quiz_status,
                expert_id=current_user.id,
            )
            db.session.add(add_q)
            db.session.commit()
        return redirect(url_for("views.home"))
        flash("Added successfully", category="Success")
    return render_template("assign_quiz.html", expert=current_user)


from flask import render_template
from flask_login import current_user
from sqlalchemy import text


@auth.route("/manage_student")
def manage_student():
    specialization = current_user.specialization

    # Fetch course IDs based on expert's specialization
    course_ids = (
        db.session.query(Course.id)
        .join(Expert, Course.id == Expert.course_id)
        .filter(Expert.specialization == specialization)
        .all()
    )
    course_ids = [course_id for course_id, in course_ids]

    # Fetch user IDs from Startcourse table based on course IDs
    user_ids = (
        Startcourse.query.filter(Startcourse.courseid.in_(course_ids))
        .with_entities(Startcourse.userid)
        .all()
    )
    user_ids = [user_id for user_id, in user_ids]

    # Fetch user records from User table based on user IDs
    users = User.query.filter(User.id.in_(user_ids)).all()

    return render_template("manage_student.html", expert=current_user, users=users)


@auth.route("/manage_quiz")
def manage_quiz():
    quiz = (
        db.session.query(Quiz.title, Quiz.time_limit, Quiz.status)
        .filter_by(expert_id=current_user.id)
        .distinct(Quiz.title)
        .all()
    )
    if not quiz:
        abort(403)
    return render_template("manage_quiz.html", quiz=quiz, expert=current_user)


@auth.route("/manage_task")
def manage_task():
    task = Task.query.filter_by(expert_id=current_user.id).all()
    if not task:
        abort(403)
    return render_template("manage_task.html", task=task, expert=current_user)


@auth.route("/progress", methods=["GET", "POST"])
def progress():
    expert_id = (
        current_user.id
    )  # Replace this with the actual way you retrieve the expert's ID

    # Step 2: Query the Quiz table to fetch quiz titles
    quiz_titles = (
        Quiz.query.filter_by(expert_id=expert_id)
        .with_entities(Quiz.title)
        .distinct()
        .all()
    )

    # Step 3: Extract quiz titles from the query results
    quiz_titles = [title for (title,) in quiz_titles]

    # Step 4: Query the Quiz_Result table using quiz titles
    quiz_results = quiz_Result.query.filter(
        quiz_Result.quiz_title.in_(quiz_titles)
    ).all()

    # Create a dictionary to store unique quiz results for each quiz title
    results = {}
    for quiz_result in quiz_results:
        quiz_title = quiz_result.quiz_title
        if quiz_title not in results:
            results[quiz_title] = []

        result = {
            "quiz_title": quiz_title,
            "userid": quiz_result.userid,
            "percentage": quiz_result.percentage,
        }
        results[quiz_title].append(result)

    # Convert results to JSON format
    results_json = json.dumps(results)

    return render_template(
        "Progress.html",
        results=results_json,
        quiz_titles=quiz_titles,
        expert=current_user,
    )


@auth.route("/performance", methods=["GET", "POST"])
def performance():
    expert_id = (
        current_user.id
    )  # Replace this with the actual way you retrieve the expert's ID

    # Step 2: Query the Quiz table to fetch quiz titles
    quiz_titles = (
        Quiz.query.filter_by(expert_id=expert_id)
        .with_entities(Quiz.title)
        .distinct()
        .all()
    )

    # Step 3: Extract quiz titles from the query results
    quiz_titles = [title for (title,) in quiz_titles]

    # Step 4: Query the Quiz_Result table using quiz titles
    quiz_results = quiz_Result.query.filter(
        quiz_Result.quiz_title.in_(quiz_titles)
    ).all()

    total_percentage = sum(result.percentage for result in quiz_results)
    average_percentage = (
        total_percentage / len(quiz_results) if len(quiz_results) > 0 else 0
    )
    # print(average_percentage)

    existing_performance = Performance.query.filter_by(expertid=current_user.id).first()
    if not existing_performance:
        # Add average performance for the user
        add_avg = Performance(overall=average_percentage, expertid=current_user.id)
        db.session.add(add_avg)
        db.session.commit()

    return render_template(
        "performance.html",
        quiz=quiz_results,
        average_percentage=average_percentage,
        expert=current_user,
    )


@auth.route("/joinchat", methods=["GET", "POST"])
def joinchat():
    specialization = current_user.specialization

    # Fetch course IDs based on expert's specialization
    course_ids = (
        db.session.query(Course.id)
        .join(Expert, Course.id == Expert.course_id)
        .filter(Expert.specialization == specialization)
        .all()
    )
    course_ids = [course_id for course_id, in course_ids]

    # Fetch user IDs from Startcourse table based on course IDs
    user_ids = (
        Startcourse.query.filter(Startcourse.courseid.in_(course_ids))
        .with_entities(Startcourse.userid)
        .all()
    )
    user_ids = [user_id for user_id, in user_ids]

    # Fetch user records from User table based on user IDs
    users = User.query.filter(User.id.in_(user_ids)).all()

    return render_template("join_chat.html", expert=current_user, users=users)


@auth.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        msg = request.form.get("msg")
        uid = request.form.get("userid")
        print(uid)
        if uid and msg:
            chat = Msg(
                msg=msg, sender=current_user.name, userid=uid, expertid=current_user.id
            )
            db.session.add(chat)
            db.session.commit()
            flash("Message sent successfully", category="success")
        else:
            flash("Error From Server", category="error")
    else:  # Handle GET request
        uid = request.args.get("userid")

    user = User.query.filter_by(id=uid).first()
    expert = current_user
    messages = Msg.query.filter(
        Msg.userid == uid, Msg.expertid == current_user.id
    ).all()

    return render_template("chat.html", user=user, messages=messages, expert=expert)


@auth.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if email is not None:
            email = email.strip()

            if password == password2:
                expert = Expert.query.filter_by(email=email).first()
                print(email)
                print(expert)

                if expert:
                    expert.password = generate_password_hash(password, method="sha256")
                    db.session.commit()
                    flash("Password changed successfully", category="success")
                    return redirect(url_for("auth.login"))
                else:
                    flash("Expert not found", category="error")
            else:
                flash("Please enter the same password twice", category="error")
        else:
            flash("Email is missing", category="error")

    return render_template("forgot.html")
