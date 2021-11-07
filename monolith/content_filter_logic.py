from monolith.database import db, User
from profanity_filter import ProfanityFilter

from flask_login import current_user


class ContentFilterLogic:

    def __init__(self):
        pass

    def toggle_filter(self, is_filter_enabled):
        db.session.query(User).filter(User.id == current_user.id)\
            .update({'content_filter_enabled': is_filter_enabled})
        db.session.commit()
        return

    def check_message_content(self, content):
        pf = ProfanityFilter()
        return pf.censor(content)
        
    def check_all_past_messages(): 
        pass
