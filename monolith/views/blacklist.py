from flask import Blueprint, redirect, render_template, request, abort
from monolith import list_logic
from monolith import blacklist_logic
from monolith.blacklist_logic import BlacklistLogic

from monolith.database import User, Blacklist, db
from monolith.forms import UnblockForm
from monolith.list_logic import ListLogic
from monolith.blacklist_logic import BlacklistLogic

from flask_login import current_user

blacklist = Blueprint('blacklist', __name__)

list_logic = ListLogic()
blacklist_logic = BlacklistLogic()

@blacklist.route('/blacklist',methods=['GET'])
def retrieve_blacklist():

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        blacklist = blacklist_logic.retrieving_blacklist(current_user.id)
        users = list_logic.retrieving_users(current_user.id)

        return render_template('blacklist.html', blacklist = blacklist, users = users)
    else:
        # there is no logged user, redirect to login
        return redirect('/login')


@blacklist.route('/block', methods=['POST'])
def _block_user():

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        target = 0
        try:
            # retrieve the user id from the form
            target = request.form.get('user_id', type=int)
        except:
            abort(500)  # internal server error

        # checking that we are not trying to block ourselves
        if current_user.id == target:
            abort(400)  # bad request

        # checkig if the given id is the id of an existing user
        if blacklist_logic.check_existing_user(target):
            blacklist_logic.add_to_blackist(current_user.id,target)
            return redirect('/blacklist')
        else:
            abort(400,'You are trying to block a non existing user!')

    else:
        # there is no logged user, redirect to login
        return redirect('/login')

@blacklist.route('/unblock', methods=['POST'])
def _unblock_user():

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        target = 0
        try:
            # retrieve the user id from the form
            target = request.form.get('user_id', type=int)
        except:
            abort(500)  # internal server error

        # checking that we are not trying to unblock ourselves
        if current_user.id == target:
            abort(400) # bad request

        # checkig if the given id is the id of an existing user
        if blacklist_logic.check_existing_user(target):

            if not blacklist_logic.delete_from_blacklist(current_user.id, target):
                abort(500) # internal server error

            return redirect('/blacklist')
        else:
            abort(400, 'You are trying to block a non existing user!')

    else:
        # there is no logged user, redirect to login
        return redirect('/login')