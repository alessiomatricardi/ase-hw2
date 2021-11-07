from flask import Blueprint, redirect, render_template, request, abort

from monolith.database import User, db
from monolith.forms import ContentFilterForm, UserForm, BlockForm
from monolith.content_filter_logic import ContentFilterLogic
from monolith.list_logic import ListLogic

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
                        please register with another email."                                                                                                                                                                                                                                                                                                                                                                                                                                    )
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

#@users.route('/profile/picture/update', methods=['GET', 'POST'])
