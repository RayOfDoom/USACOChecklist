import json
from datetime import date
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import ChecklistEntry

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html", user=current_user)


@views.route('/problems')
@login_required
def problems():
    return render_template("problems.html", user=current_user)


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
