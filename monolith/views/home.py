from flask import Blueprint, render_template, redirect, request
from flask.helpers import url_for
from monolith.auth import current_user
from monolith.content_filter_logic import ContentFilterLogic
from monolith.database import db, User
home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome = welcome)

# show the account information
@home.route('/account_info', methods=['GET','POST'])
def account_info():
    if request.method == 'GET':
        if current_user is not None and hasattr(current_user, 'id'):
            # show user informations
            return render_template("account_info.html")
        else:
            # TODO
            # user does not exists
            return redirect("/login")

    elif request.method == 'POST':

        return redirect(url_for('.content_filter'))

@home.route('/account_info/content_filter', methods=['GET'])
def content_filter():
    cfl = ContentFilterLogic()

    user = User()
  
    user = db.session.query(User).filter(User.id == current_user.id).first()
    print("this is user object")
    print(user)

    if user.content_filter_enabled == True:
        cfl.de_activate_filter(user.id)
        msg = "Your content filter has been deactivated"

    elif user.content_filter_enabled == False:
        cfl.activate_filter(user.id)
        msg = "Your content filter has been activated"    

    return render_template('content_filter.html', messages = msg)