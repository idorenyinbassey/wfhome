from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from . import auth
from models import User, db  # Correct import assuming you're using relative imports

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)  # Use set_password to hash the password
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find the user by email or username
        user = User.query.filter(
            (User.email == form.login_identifier.data) |
            (User.username == form.login_identifier.data)
        ).first()
        # Check if user exists and password matches (assumes password hashing)
        if user and user.check_password(form.password.data):  # Implement check_password in User model
            login_user(user)
            return redirect(url_for('tasks.dashboard'))
        else:
            flash('Login unsuccessful. Please check your credentials.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))