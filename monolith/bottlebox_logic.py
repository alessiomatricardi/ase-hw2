from pydantic.errors import MissingError
from monolith.content_filter_logic import ContentFilterLogic
from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist

import datetime


class BottleBoxLogic:

    def __init__(self):
        pass

    def retrieving_all_users(self):
        return db.session.query(User).where(User.is_admin == False)

    # utility to retrieve messages from db: type 1 for pending, type 2 for received, type 3 for delivered
    def  retrieving_messages(self,user_id,type):

        user = db.session.query(User).filter(User.id == user_id).first()
        
        filter = ContentFilterLogic()

        today = datetime.datetime.now()

        if type == 1: #pending
            msg = db.session.query(Message).where(Message.sender_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == False).where(Message.deliver_time > today)
            
            #if the content filter is active, all the messages will be displayed censored
            if user.is_active:
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content
            
            return msg
        elif type == 2: #received
            msg = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id).where(Message_Recipient.recipient_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)

            if user.is_active:
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content
            return msg
        elif type == 3: #delivered
            msg = db.session.query(Message).where(Message.sender_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)

            if user.is_active:
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content

            return msg
