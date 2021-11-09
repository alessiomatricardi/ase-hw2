# this class contains all the logic required to handle messages
from monolith.database import db, User
from datetime import datetime
from werkzeug.security import check_password_hash


class UserLogic:
    
    def __init__(self):
        pass


    # get that user
    def get_user(self, user_id):
        
        user = User()

        user = db.session.query(User).filter(User.id == user_id).first()

        return user


    # modify the data personal data of a user and return true or false depending on the fact that the update went well or not
    def modify_personal_data(self, user_id, form):

        try:
            db.session.query(User).filter(User.id == user_id).update({'firstname': form['firstname']})
            db.session.query(User).filter(User.id == user_id).update({'lastname': form['lastname']})
            db.session.query(User).filter(User.id == user_id).update({'date_of_birth': datetime.strptime(form['date_of_birth'], '%Y-%m-%d').date()})           
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    

    def check_form_password(self, user_id, old_password, new_password, repeat_new_password):
        
        # retrieve the user from the database
        user = db.session.query(User).filter(User.id == user_id).first()
 
        # check if the old password is the same of the one stored in the database
        if not check_password_hash(user.password, old_password):
            return 1 # this value is handled in the view

        # check that the old and new password are not the same
        if check_password_hash(user.password, new_password):
            return 2 # this value is handled in the view

        # check that the new password and the repeated new password are different
        if new_password != repeat_new_password:
            return 3 # this value is handled in the view

        return 0 # no errors
    

    def modify_password(self, user_id, new_password):

        # retrieve the user from the database
        user = db.session.query(User).filter(User.id == user_id).first()

        # set the new password
        user.set_password(new_password)
        db.session.commit()