from flask import Blueprint, redirect, render_template, abort
from flask_login import login_user, logout_user

from monolith.database import User, db
from monolith.forms import LoginForm
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if the user is already logged in, redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        return redirect('/')
    
    form = LoginForm() 
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.is_active and user.authenticate(password):
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    # if the user is not logged in, don't logout and directly redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        logout_user()
    
    return redirect('/')
