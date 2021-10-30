from flask import Blueprint, redirect, render_template, request, abort
from monolith.blacklist_logic import BlacklistLogic

from monolith.database import User, Blacklist, db
from monolith.list_logic import ListLogic
from monolith.blacklist_logic import BlacklistLogic

from flask_login import current_user

block_user = Blueprint('block_user', __name__)

ll = ListLogic()
bll = BlacklistLogic()

@block_user.route('/blacklist',methods=['GET'])
def retrieve_blacklist():
    
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        blacklist = bll.retrieving_blacklist(current_user.id)
        users = ll.retrieving_users(current_user.id)
        return render_template('blacklist.html', blacklist = blacklist, users = users)
    else:
        # there is no logged user, redirect to login
        return redirect('/login')


@block_user.route('/block_user', methods=['GET'])
def blocking():

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        
        target = request.args.get('target')

        # checkig if the given id is the id of an existing user
        if bll.check_existing_user(target):
            bll.add_to_blackist(current_user.id,target)
            return redirect('/blacklist')
        else:
            abort(400,'You are trying to block a non existing user!')

    else:
        # there is no logged user, redirect to login
        return redirect('/login')