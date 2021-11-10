from flask import Blueprint, redirect, render_template, request, abort
from flask.helpers import flash
from flask_login import logout_user
from werkzeug.security import check_password_hash
from flask.helpers import send_from_directory
import os

from monolith.database import User, db
from monolith.forms import ContentFilterForm, ProfilePictureForm, UserForm, BlockForm, ModifyPersonalDataForm, ModifyPasswordForm, UnregisterForm, SearchUserForm
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
            
            # checking if the given email has already been used and aborting if so
            try:
                check_existing_user(new_user.email)
            except EmailAlreadyUsedError:
                # this add an error message that will be printed on screen
                form.email.errors.append(new_user.email + " is not available, please register with another email.")
                return render_template('register.html', form=form)

            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        # validation failed, when the page reloads it will show the specific error message
        return render_template('register.html', form=form)
    else:
        return render_template('register.html', form=form)
    """else:
        raise RuntimeError('This should not happen!')"""


@users.route('/unregister', methods=['GET', 'POST'])
def _unregister():

    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        form = UnregisterForm()
        # using a form to verify authenticity of the unregistration request through password
        if form.validate_on_submit():
            password = form.data['password']
            q = db.session.query(User).where(User.id == current_user.id)
            user = q.first()

            # if the password is correct, the user won't be active anymore
            # the user is not going to be deleted from db because there may be pending messages to be sent from this user
            password_is_right = check_password_hash(user.password, password)
            if password_is_right:
                user.is_active = False
                db.session.commit()
                logout_user()
                return redirect('/')

        # html template for unregistration confirmation
        return render_template('unregister.html', form=form, user=current_user)

    else:
        return redirect('/login')

# retrieve the list of all users
@users.route('/users', methods=['GET'])
def _users():
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        list_logic = ListLogic()

        recipients = list_logic.retrieving_recipients(current_user.id)

        # rendering the template
        # update result whit template
        return render_template("users.html", users=recipients)

    else:
        return redirect('/login')


@users.route('/users/<user_id>', methods=['GET'])
def _user_details(user_id):
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        # get the user id
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


@users.route('/users/<user_id>/picture', methods=['GET'])
def _get_profile_photo(user_id):
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        # get the user id
        # if <id> is not a number, render 404 page
        try:
            user_id = int(user_id)
        except:
            abort(404)

        list_logic = ListLogic()

        if user_id != current_user.id:
            # blocked or blocking users can't see this image
            all_recipients = [ob.id for ob in list_logic.retrieving_recipients(current_user.id)]
            if user_id not in all_recipients:
                abort(403)

        user_logic = UserLogic()

        # get the user
        user = user_logic.get_user(user_id)

        filename = 'default'

        # if has picture, then his filename is <id>.jpeg
        if (user.has_picture):
            filename = str(user_id)

        dimension = request.args.get('dim')

        # if dim=small then filename is <id>_100.jpeg
        if dimension == 'small':
            filename += "_100"

        filename += ".jpeg"

        return send_from_directory(os.path.join(os.getcwd(), 'monolith', 'static', 'pictures'), filename)

    else:
        return redirect('/login')


# show the account information
@users.route('/profile', methods=['GET'])
def _show_profile():
    # checking if there is a logged user, otherwise redirect to login
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
    # checking if there is a logged user, otherwise redirect to login
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

        else:
            return redirect('/profile')

    else:
        return redirect("/login")


@users.route('/profile/picture/edit', methods=['GET', 'POST'])
def _modify_profile_picture():

    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        form = ProfilePictureForm()

        if request.method == 'GET':
            

            return render_template('modify_picture.html', form = form)

        else:

            if form.validate_on_submit():

                # be sure that the file is an image
                user_logic = UserLogic()

                # retrieve image
                image = request.files['image']

                if not user_logic.validate_picture(image):
                    form.image.errors.append("This file format is not supported")

                    return render_template('modify_picture.html', form=form)

                try:
                    # retrieve the image
                    img_data = form.image.data

                    # save image in 256x256
                    img = Image.open(img_data)
                    img = img.convert('RGB') # in order to support also Alpha transparency images such as PNGs
                    img = img.resize([256, 256], Image.ANTIALIAS)
                    img.save('./monolith/static/pictures/' + str(current_user.id) +
                                '.jpeg', "JPEG", quality=100, subsampling=0)

                    # save image in 100x100
                    img = Image.open(img_data)
                    img = img.convert('RGB')  # in order to support also Alpha transparency images such as PNGs
                    img = img.resize([100, 100], Image.ANTIALIAS)
                    img.save('./monolith/static/pictures/' + str(current_user.id) +
                                '_100.jpeg', "JPEG", quality=100, subsampling=0)

                    # now the user has a personal profile picture
                    user = User()
                    user = db.session.query(User).filter(User.id == current_user.id).first()
                    user.has_picture = 1
                    db.session.commit()
                
                except Exception:
                    abort(500)

                return redirect('/profile')

            # if the form is not valid, the modify_picture.html page is rendered again
            else:
                return render_template('modify_picture.html', form = form)

    else:
        return redirect('/login')


@users.route('/profile/data/edit', methods=['GET', 'POST'])
def _modify_personal_data():
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        form = ModifyPersonalDataForm()

        if request.method == 'GET':

            # populate the form with the existing data of the user
            form.firstname.data = current_user.firstname
            form.lastname.data = current_user.lastname
            form.date_of_birth.data = current_user.date_of_birth

            return render_template('modify_personal_data.html', form=form)
        
        elif request.method == 'POST':
            
            if not form.validate_on_submit():
                return render_template('modify_personal_data.html', form=form)

            user_logic = UserLogic()

            # if user data are correctly modified
            if user_logic.modify_personal_data(current_user.id, request.form):
                return redirect('/profile')
            
            # something went wrong in the modification of the personal data
            return render_template('modify_personal_data.html', form=form)

    else:
        return redirect('/login')


@users.route('/profile/password/edit', methods=['GET', 'POST'])
def _modify_password():
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        form = ModifyPasswordForm()
        
        if request.method == 'GET':

            return render_template('modify_password.html', form=form)
        
        elif request.method == 'POST':

            if not form.validate_on_submit():
                return render_template('modify_password.html', form=form)

            user_logic = UserLogic()

            # check if the old password is the same of the one stored in the database
            # check that the old and new password are not the same
            # check that the new password and the repeated new password are equal
            old_password = form.old_password.data
            new_password = form.new_password.data
            repeat_new_password = form.repeat_new_password.data
            result = user_logic.check_form_password(current_user.id, old_password, new_password, repeat_new_password)

            if result == 0:
                # proceed to the modification of the password
                user_logic.modify_password(current_user.id, new_password)

                return redirect('/profile')

            if result == 1:
                form.old_password.errors.append(
                    "The old password you inserted is incorrect. Please insert the correct one.")
            if result == 2:
                form.new_password.errors.append(
                    "Please insert a password different from the old one.")
            if result == 3:
                form.repeat_new_password.errors.append(
                    "The new password and its repetition must be equal.")
                
            return render_template('modify_password.html', form=form)
                
    else:
        return redirect('/login')


@users.route('/users/search', methods=['GET', 'POST'])
def _search_user():
    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):
        
        form = SearchUserForm()
        
        if request.method == 'GET':
            return render_template('search_user.html', form=form)

        else:

            form = request.form
            firstname, lastname, email = form['firstname'], form['lastname'], form['email']

            list_logic = ListLogic()

            # if none of the fileds have been compiled
            if not firstname and not lastname and not email:
                flash("Insert at least one field")
                return redirect('/users/search')

            else:
                # retrieving the list of users that match with the content of the form
                users = list_logic.search_user_form(list_logic.retrieving_recipients(current_user.id), firstname, lastname, email)

                if not users:
                    flash("No user found")
                    return redirect('/users/search')
                
                else:
                    return render_template("users.html", users=users)

    else:
        return redirect('/login')