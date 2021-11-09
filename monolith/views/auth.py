from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user

from monolith.database import User, db
from monolith.forms import LoginForm
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def _login():
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
                "Account " + email + " does not exist."
            )
            return render_template('login.html', form=form)
        
        authenticated = user.authenticate(password)

        if user.is_active and authenticated:
            # login the user
            login_user(user)
            return redirect('/')
        elif not user.is_active:
            # the user unregistered his profile
            # this add an error message that will be printed on screen
            form.email.errors.append(
                "This account is no longer active."
            )
        else:
            # wrong password
            # this add an error message that will be printed on screen
            form.password.errors.append(
                "Password is wrong."
            )

    return render_template('login.html', form=form)


@auth.route("/logout")
def _logout():
    # if the user is not logged in, don't logout and directly redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        logout_user()
    
    return redirect('/')
