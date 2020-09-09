import os
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from vfinance.extensions import db
from vfinance.forms import LoginForm, RegisterForm
from vfinance.models import User
from vfinance.utils import redirect_back
from sqlalchemy.exc import IntegrityError



auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cash = 1000000
        user = User(
            username = username,
            cash = cash,
            position = 0
        )
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            flash("Thanks for registering! Please login!", 'success' )
            
        except IntegrityError:
            flash("Account already exists", 'danger')
            db.session.rollback()
            return redirect_back()
        return redirect(url_for('home.index'))
        

    return render_template("auth/register.html", form = form)



@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        # flash('You are already loging','success')
        return redirect(url_for("home.index"))
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        users = User.query.all()
        
        for user in users:
            if username in user.username:
                if user.validate_password(password):
                    login_user(user,remember)
                    flash('Welcome Back '+user.username, 'info')
                    return redirect_back()
                # flash("Invalid username or password.", 'warning')
                else:
                    flash("Invalid username or password.", 'warning')
            
                
       
    return render_template("auth/login.html", form = form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
