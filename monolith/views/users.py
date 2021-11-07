from datetime import date, datetime
from operator import methodcaller
from flask import Blueprint, redirect, render_template, request, abort
from flask.signals import message_flashed
from flask_wtf import form

from monolith.database import User, db
from monolith.forms import ContentFilterForm, UserForm, BlockForm, ModifyPersonalDataForm
from monolith.content_filter_logic import ContentFilterLogic
from monolith.user_logic import UserLogic

from flask_login import current_user

# defining exception error for handling the registration with duplicate email
class EmailAlreadyUsedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# utility function to check if the email inserted in the form has already been used in a previous registration
def check_existing_user(email):
    check = db.session.query(User).where(User.email == email).count()

    if check != 0:
        raise EmailAlreadyUsedError('You must use a different email, this one has already been used')
    else:
        return None

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST', 'GET'])
def _register():
    # if the user is already logged in, redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        return redirect('/')

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

            # checking if the given email has already been used and aborting if so
            try:
                check_existing_user(new_user.email)
            except EmailAlreadyUsedError:
                # this add an error message that will be printed on screen
                form.email.errors.append(new_user.email + " is not available, \
                        please register with another email."                                                                                                                                                                                                                                                )
                return render_template('register.html', form=form)

            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
        # validation failed, when the page reloads it will show the specific error message
        return render_template('register.html', form=form)
    elif request.method == 'GET':
        return render_template('register.html', form=form)
    else:
        raise RuntimeError('This should not happen!')


# retrieve the list of all users
@users.route('/users', methods=['GET'])
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)


@users.route('/users/<user_id>', methods=['GET'])
def _user_details(user_id):
    # get the user
    # if <id> is not a number, render 404 page
    try:
        user_id = int(user_id)
    except:
        abort(404)

    # if the user is logged in and try to access this page, redirect him to /profile
    if current_user is not None and hasattr(current_user, 'id'):
        if (current_user.id == user_id):
            return redirect('/profile')

    # retrieve user from the database
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        abort(404)

    block_form = BlockForm(user_id = user.id)

    # render the page
    return render_template('user_details.html', user = user, block_form = block_form)


# show the account information
@users.route('/profile', methods=['GET'])
def _show_profile():
    if current_user is not None and hasattr(current_user, 'id'):

        content_filter_form = ContentFilterForm(
            filter_enabled=current_user.content_filter_enabled)

        # show user informations
        return render_template("user_details.html",
                               user=current_user,
                               content_filter_form = content_filter_form)
    else:
        return redirect("/login")


@users.route('/profile/content_filter', methods=['POST'])
def _content_filter():
    if current_user is not None and hasattr(current_user, 'id'):

        form = ContentFilterForm()

        if form.validate_on_submit():

            # get data from the form
            is_filter_enabled = form.filter_enabled.data

            filter_logic = ContentFilterLogic()

            user = User()

            # retrieve the user
            user = db.session.query(User).filter(User.id == current_user.id).first()

            # use logic to toggle the content filter
            filter_logic.toggle_filter(is_filter_enabled)

            return redirect('/profile')

            return render_template('user_details.html',
                                   user=current_user,
                                   content_filter_form = form)

        else:
            return redirect('/profile')

    else:
        abort(403) # no one apart of the logged user can do this action

#@users.route('/profile/picture/update', methods=['GET', 'POST'])

@users.route('/profile/modify_personal_data', methods=['GET', 'POST'])
def modify_personal_data():
    if current_user is not None and hasattr(current_user, 'id'):

        # TODO if needed, create an instance of UserLogic

        if request.method == 'GET':
            form = ModifyPersonalDataForm()

            # populate the form with the existing data of the user
            form.firstname.data = current_user.firstname
            form.lastname.data = current_user.lastname

            return render_template('modify_personal_data.html', form=form, date_of_birth=current_user.date_of_birth)
        
        elif request.method == 'POST':

            user_logic = UserLogic()

            form = request.form

            if user_logic.modify_personal_data(current_user.id, form):
                # TODO check if current_user has been updated (eventually update it)

                return redirect('/profile')

            else: # something went wrong in the modification of the personal data
                # TODO handle the incorrect modification of data
                return redirect('/profile')

        
        else:
            raise RuntimeError('This should not happen!')

    else:
        abort(403) # no one apart of the logged user can do this action