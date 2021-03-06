import uuid

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, UserExtras
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        password0 = request.form.get('password0')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=current_user.username).first()
        if not check_password_hash(user.password, password0):
            flash('Incorrect password, try again.', category='error')
        elif password0 == password1:
            flash('New password must be different than old password.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('New password must be at least 7 characters.', category='error')
        else:
            user.password = generate_password_hash(password1, method='sha256')
            db.session.commit()
            flash('Password successfully changed!', category='success')
            return redirect(url_for('auth.logout'))

    return render_template("change_password.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Account does not exist.', category='error')
        elif not check_password_hash(user.password, password):
            flash('Incorrect password, try again.', category='error')
        else:
            user_extras = UserExtras.query.filter_by(id=user.id).first()
            if not user_extras:
                add_user_extras(user)

            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            add_user_extras(new_user)
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


def add_user_extras(user):
    user_extra = UserExtras(id=user.id, unique_key=str(uuid.uuid4()).replace('-', ''), diff_pref=0)
    db.session.add(user_extra)
    db.session.commit()
