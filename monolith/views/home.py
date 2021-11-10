from flask import Blueprint, render_template, redirect, request
from flask.helpers import url_for
from monolith.auth import current_user
from monolith.content_filter_logic import ContentFilterLogic
from monolith.database import db, User
home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def _index():
    # render the homepage
    return render_template("index.html")