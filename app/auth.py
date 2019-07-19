from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required, logout_user
from .controls import User
from .utils import exception_message
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        remember = True if request.form.get('remember') else False
        try:
            user = User(
                username=request.form.get('username'),
                password=request.form.get('password'),
            )
        except Exception as e:
            flash(exception_message(e))
            return redirect(url_for('auth.login'))

        return redirect(url_for('main.notes'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        password = request.form.get('password')
        try:    
            user = User(
                email=request.form.get('email'),
                username=request.form.get('name'),
                password=request.form.get('password')
            )
            user.create()
        except Exception as e:
            flash(exception_message(e))
            return render_template('signup.html')

        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


