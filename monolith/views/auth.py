from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

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

        # the user doesn't exists
        if user is None:
            # this add an error message that will be printed on screen
            form.email.errors.append(
                "Account '" + user.email + "' doesn't exists."
            )
            return render_template('login.html', form=form)
        
        password_is_right = check_password_hash(user.password, password)

        if user.is_active and password_is_right:
            # login the user
            login_user(user)
            return redirect('/')
        elif not user.is_active:
            # the user unregistered his profile
            # this add an error message that will be printed on screen
            form.email.errors.append(
                "This account is no longer available."
            )
        elif not password_is_right:
            # wrong password
            # this add an error message that will be printed on screen
            form.password.errors.append(
                "Password is wrong."
            )

    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    # if the user is not logged in, don't logout and directly redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        logout_user()
    
    return redirect('/')
