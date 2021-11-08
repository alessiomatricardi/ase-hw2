# this class contains all the logic required to handle messages
from sqlalchemy.sql.functions import user
from wtforms.form import FormMeta
from monolith.database import db, User
from sqlalchemy import func
from datetime import date, datetime


class UserLogic:
    
    def __init__(self):
        pass

    # create a STRING of recipients' emails to be used when sending a message
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
        if user.authenticate(old_password) == False:
            return 1 # this value is handled in the view

        # check that the old and new password are not the same
        if user.authenticate(old_password) == user.authenticate(new_password):
            return 2 # this value is handled in the view

        # check that the new password and the repeated new password are different
        if new_password != repeat_new_password:
            return 3 # this value is handled in the view

        return 4 # no errors
    
    def modify_password(self, user_id, new_password):

        # retrieve the user from the database
        user = db.session.query(User).filter(User.id == user_id).first()

        # set the new password
        user.set_password(new_password)
        db.session.commit()