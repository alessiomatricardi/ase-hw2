# this class contains all the logic required to handle messages
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
            print(5)
            db.session.rollback()
            return False