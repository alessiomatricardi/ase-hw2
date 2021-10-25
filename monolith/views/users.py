from flask import Blueprint, redirect, render_template, request, abort

from monolith.database import User, db
from monolith.forms import UserForm

class EmailAlreadyUsedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def check_existing_user(email):
    check = db.session.query(User).where(User.email == email).count()

    if check != 0:
        raise EmailAlreadyUsedError('You must use a different email, this one has already been used')
    else:
        return None



users = Blueprint('users', __name__)

@users.route('/users')
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """
            Password should be hashed with some salt. For example if you choose a hash function x, 
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            try:
                check_existing_user(new_user.email)
            except EmailAlreadyUsedError:
                abort(400,"This email has already been used in a previous registration, please register with another email.") 

            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')
