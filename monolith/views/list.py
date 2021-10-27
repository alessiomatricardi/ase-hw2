from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist
from monolith.forms import UserForm
from monolith.auth import current_user
from monolith.list_logic import ListLogic

list = Blueprint('list', __name__)

@list.route('/recipients_list',methods=['GET'])
def users_list():
       
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        
        list_logic = ListLogic()

        recipients = list_logic.retrieving_recipients(current_user.id)

        # rendering the template
        # update result whit template
        return render_template("recipients_list.html", users=recipients)
    
    else:
        # there is no logged user, redirect to login
        return redirect('/login')