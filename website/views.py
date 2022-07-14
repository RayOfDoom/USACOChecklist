import json
from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import ChecklistEntry, Problem, User, UserExtras

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
    return render_template("problems.html", user=current_user, problems=json.dumps(problemlist), checklist=json.dumps(checklist))


@views.route('/update_problems/<string:probleminfo>', methods=['POST'])
@login_required
def update_problems(probleminfo):
    probleminfo = json.loads(probleminfo)
    pid = probleminfo['pid']
    status = probleminfo['status']

    oldentry = current_user.get_status(pid)
    if oldentry:
        oldentry.date = date.today()
        oldentry.progress = status
    else:
        newentry = ChecklistEntry(user_id=current_user.id, pid=pid, date=date.today(), progress=status)
        db.session.add(newentry)
    db.session.commit()
    return ("/")


@views.route('/view/<string:userhash>')
def share(userhash):
    user = User.query.filter_by(id=UserExtras.query.filter_by(unique_key=userhash).first().id).first()
    if not user:
        return redirect(url_for(views.home))
    problemlist = []
    for problem in Problem.query.order_by(Problem.pid.desc()).all():
        problemlist.append(problem.as_dict())
    checklist = []
    for entry in user.checklist.all():
        checklist.append(entry.as_dict())
    return render_template("view_list.html", user=current_user, list_author=user, problems=json.dumps(problemlist), checklist=json.dumps(checklist))
