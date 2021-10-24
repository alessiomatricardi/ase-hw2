from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist
from monolith.forms import UserForm
from monolith.auth import current_user

list = Blueprint('list', __name__)

@list.route('/recipients_list',methods=['GET'])
def users_list():
       
    # checking if there'is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        
        # retrieving the list of non admin users, active users, without current_user 
        all_users = db.session.query(User).where(User.is_admin == False).where(User.id != current_user.id).where(User.is_active != False)
        all_users = [a for a in all_users]

        # retrieving the list of blacklist instances in which current_user is involved
        blacklist = db.session.query(Blacklist).where(Blacklist.blocking_user_id == current_user.id or Blacklist.blocked_user_id == current_user.id)
        blacklist = [b for b in blacklist]
        
        for blacklist_instance in blacklist:
            
            # getting from the blacklist the users that blocked the current user and deleting them from users list
            if blacklist_instance.blocked_user_id == current_user.id:
                for blocking_user in all_users:
                    if blocking_user.id == blacklist_instance.blocking_user_id:
                        all_users.remove(blocking_user)
                        break

            # getting from the blacklist the blocked users and deleting them from users list
            if blacklist_instance.blocking_user_id == current_user.id:
                for blocked_user in all_users:
                    if blocked_user.id == blacklist_instance.blocked_user_id:
                        all_users.remove(blocked_user)
                        break
        
        # rendering the template
        # update result whit template
        return render_template("recipients_list.html", users=all_users)
    
    else:
        # there is no logged user, redirect to login
        return redirect('/login')