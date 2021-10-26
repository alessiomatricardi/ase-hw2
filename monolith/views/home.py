from flask import Blueprint, render_template, redirect

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        welcome = "Logged In!"
    else:
        welcome = None
    return render_template("index.html", welcome = welcome)

# show the account information
@home.route('/account_info')
def account_info():
    if current_user is not None and hasattr(current_user, 'id'):
        # show user informations
        return render_template("account_info.html")
    else:
        # TODO
        # user does not exists
        return redirect("/login")