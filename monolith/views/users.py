from datetime import date, datetime
from operator import methodcaller
from flask import Blueprint, redirect, render_template, request, abort
from flask.helpers import url_for, flash
from flask.signals import message_flashed
from flask_wtf import form

from monolith.database import User, db
from monolith.forms import ContentFilterForm, ProfilePictureForm, UserForm, BlockForm, ModifyPersonalDataForm, ModifyPasswordForm
from monolith.content_filter_logic import ContentFilterLogic
from monolith.list_logic import ListLogic
from monolith.user_logic import UserLogic
from PIL import Image

from flask_login import current_user

# TODO MOVE THESE FUNCTIONS INSIDE USER LOGIC

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
                        please register with another email."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    )
                return render_template('register.html', form=form)

            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        # validation failed, when the page reloads it will show the specific error message
        return render_template('register.html', form=form)
    elif request.method == 'GET':
        return render_template('register.html', form=form)
    else:
        raise RuntimeError('This should not happen!')


# retrieve the list of all users
@users.route('/users', methods=['GET'])
def _users():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        list_logic = ListLogic()

        recipients = list_logic.retrieving_recipients(current_user.id)

        # rendering the template
        # update result whit template
        return render_template("users.html", users=recipients)

    else:
        # there is no logged user, redirect to login
        return redirect('/login')


@users.route('/users/<user_id>', methods=['GET'])
def _user_details(user_id):
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        # get the user
        # if <id> is not a number, render 404 page
        try:
            user_id = int(user_id)
        except:
            abort(404)

        # if the user is logged in and try to access this page, redirect him to /profile
        if (current_user.id == user_id):
            return redirect('/profile')

        list_logic = ListLogic()

        # retrieve user from the database
        all_recipients = [ob.id for ob in list_logic.retrieving_recipients(current_user.id)]
        if user_id not in all_recipients:
            abort(404)

        user = db.session.query(User).filter(User.id == user_id).first()

        block_form = BlockForm(user_id = user.id)

        # render the page
        return render_template('user_details.html', user = user, block_form = block_form)

    else:
        return redirect('/login')


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

@users.route('/profile/picture', methods=['GET', 'POST'])
def _profile_picture():
    if current_user is not None and hasattr(current_user, 'id'):

        if request.method == 'GET':
            form = ProfilePictureForm()

            return render_template('modify_picture.html', form = form)

        elif request.method == 'POST':
            # retrieve the form
            form = ProfilePictureForm()

            if form.validate_on_submit():

                try:

                    # be sure that the file is an image
                    # TODO

                    # retrieve the image
                    img_data = form.image.data

                    # save image in 256x256
                    img = Image.open(img_data)
                    img.resize([256, 256], Image.ANTIALIAS)
                    img.save(
                        './monolith/static/pictures/' + str(current_user.id) + 
                        '.jpg', "JPEG")

                    # save image in 100x100
                    img = Image.open(img_data)
                    img.resize([100, 100], Image.ANTIALIAS)
                    img.save(
                        './monolith/static/pictures/' + str(current_user.id) +
                        '_100.jpg', "JPEG")

                    # now the user has a personal profile picture
                    user = User()
                    user = db.session.query(User).filter(User.id == current_user.id).first()
                    user.has_picture = 1
                    db.session.commit()
                
                except Exception:
                    abort(500)

                return redirect('/profile')

            else:
                return render_template('modify_picture.html', form = form)

    else:
        return redirect('/login')
@users.route('/profile/data', methods=['GET', 'POST'])
def modify_personal_data():
    if current_user is not None and hasattr(current_user, 'id'):

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
                return redirect('/profile')

            else: # something went wrong in the modification of the personal data
                flash('Please insert correct data')
                return redirect('/profile/data')
        
        else:
            raise RuntimeError('This should not happen!')

    else:
        return redirect('/login')


@users.route('/profile/password', methods=['GET', 'POST'])
def modify_password():
    if current_user is not None and hasattr(current_user, 'id'):
        
        if request.method == 'GET':
            form = ModifyPasswordForm()
            return render_template('modify_password.html', form=form)

        
        elif request.method == 'POST':

            user_logic = UserLogic()

            form = request.form

            # check if the old password is the same of the one stored in the database
            # check that the old and new password are not the same
            # check that the new password and the repeated new password are equal
            result = user_logic.check_form_password(current_user.id, form['old_password'], form['new_password'], form['repeat_new_password'])

            if result == 1:
                flash("The old password you inserted is incorrect. Please insert the correct one.")
                return redirect('/profile/password')
            elif result == 2:
                flash("Please insert a password different from the old one.")
                return redirect('/profile/password')
            elif result == 3:
                flash("The new password and its repetition must be equal.")
                return redirect('/profile/password')
            else: 
                # proceed to the modification of the password
                user_logic.modify_password(current_user.id, form['new_password'])
                        
                return redirect('/profile')
                
    else:
        return redirect('/login')
