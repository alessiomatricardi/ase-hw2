from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
import datetime

class BottleBoxLogic:

    def __init__(self):
        pass

    def retrieving_all_users(self):
        return db.session.query(User).where(User.is_admin == False)

    # utility to retrieve messages from db: type 1 for pending, type 2 for received, type 3 for delivered
    def  retrieving_messages(self,user_id,type):

        today = datetime.datetime.now()

        if type == 1: #pending
            return db.session.query(Message).where(Message.sender_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == False).where(Message.deliver_time > today)
        elif type == 2: #received
            return Message.query.join(Message_Recipient, Message.id == Message_Recipient.id).where(Message_Recipient.recipient_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)
        elif type == 3: #delivered
            return db.session.query(Message).where(Message.sender_id == user_id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)

