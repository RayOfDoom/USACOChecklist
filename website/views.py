import json
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import Problem, User, UserExtras

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html", user=current_user)


@views.route('/problems')
@login_required
def problems():
    problemlist = []
    for problem in Problem.query.order_by(Problem.pid.desc()).all():
        problemlist.append(problem.as_dict())
    checklist = []
    for entry in current_user.checklist.all():
        checklist.append(entry.as_dict())
    problemcases = []
    for case in current_user.problem_cases.all():
        problemcases.append(case.as_dict())
    return render_template("problems.html", user=current_user, problems=json.dumps(problemlist), checklist=json.dumps(checklist), problemcases=json.dumps(problemcases))


@views.route('/view/<string:userhash>')
def view(userhash):
    user = User.query.filter_by(id=UserExtras.query.filter_by(unique_key=userhash).first().id).first()
    if not user:
        return redirect(url_for(views.home))
    problemlist = []
    for problem in Problem.query.order_by(Problem.pid.desc()).all():
        problemlist.append(problem.as_dict())
    checklist = []
    for entry in user.checklist.all():
        checklist.append(entry.as_dict())
    problemcases = []
    for case in current_user.problem_cases.all():
        problemcases.append(case.as_dict())
    return render_template("view_list.html", user=current_user, list_author=user, problems=json.dumps(problemlist), checklist=json.dumps(checklist), problemcases=json.dumps(problemcases))
