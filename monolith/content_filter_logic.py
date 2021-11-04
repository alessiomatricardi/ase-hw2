from monolith.database import db, User
from profanity_filter import ProfanityFilter



class ContentFilterLogic:

    def __init__(self):
        pass

    def activate_filter(self, user_id):
        db.session.query(User).filter(User.id == user_id).update({'content_filter_enabled': True})
        db.session.commit()
        return 
    
    def de_activate_filter(self, user_id):
        db.session.query(User).filter(User.id == user_id).update({'content_filter_enabled': False})
        db.session.commit()
        return

    def check_message_content(self, content):
        pf = ProfanityFilter()
        return pf.censor(content)
        
    def check_all_past_messages(): 
        pass
