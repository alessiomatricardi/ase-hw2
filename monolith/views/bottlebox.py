from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist
from monolith.forms import UserForm
from monolith.auth import current_user

bottlebox = Blueprint('bottlebox', __name__)

@bottlebox.route('/bottlebox',methods=['GET'])
def retrieving_bottlebox():
    
    v = request.args.get("value")
    
    if v == "home":
        return render_template('bottlebox_home.html')