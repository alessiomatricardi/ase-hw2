from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
import datetime
from sqlalchemy.sql import or_

class ListLogic:
    
    def __init__(self):
        pass

    # retrieving the list of non admin users, active users, without current_user 
    def retrieving_users(self, id):
        all_users = db.session.query(User).where(User.is_admin == False).where(User.id != id).where(User.is_active != False)
        return [a for a in all_users]

    # retrieving the list of blacklist instances in which current_user is involved
    def retrieving_users_in_blacklist(self, id):
        blacklist = db.session.query(Blacklist).where(or_(Blacklist.blocking_user_id == id, Blacklist.blocked_user_id == id))
        return [b for b in blacklist]
        
    def retrieving_recipients(self, id):
        
        all_users = self.retrieving_users(id)
        blacklist = self.retrieving_users_in_blacklist(id)

        for blacklist_instance in blacklist:
            
            # getting from the blacklist the users that blocked the current user and deleting them from users list
            if blacklist_instance.blocked_user_id == id:
                for blocking_user in all_users:
                    if blocking_user.id == blacklist_instance.blocking_user_id:
                        all_users.remove(blocking_user)
                        break

            # getting from the blacklist the blocked users and deleting them from users list
            if blacklist_instance.blocking_user_id == id:
                for blocked_user in all_users:
                    if blocked_user.id == blacklist_instance.blocked_user_id:
                        all_users.remove(blocked_user)
                        break
        
        return all_users