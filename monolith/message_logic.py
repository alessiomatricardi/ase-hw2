# this class contains all the logic required to handle messages
from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
import datetime
from .background import celery
from monolith.list_logic import ListLogic

class MessageLogic:
    
    def __init__(self):
        pass

    # create a STRING of recipients' emails to be used when sending a message
    def get_list_of_recipients_email(self, sender_id):
        
        list_logic = ListLogic()
        list_of_recipients = list_logic.retrieving_recipients(sender_id)
        return [(recipient.email, recipient.email) for recipient in list_of_recipients]


    # verifies that the message fields are consistent
    def validate_message_fields(self, message):
        if message.deliver_time < datetime.datetime.now(): # check if the datetime is correct
            message.deliver_time = datetime.datetime.now() # if it set to a past day, it is sent with current datetime

        return True 
    

    # add a new message into the database
    def create_new_message(self, message):
        
        db.session.add(message)
        db.session.commit()

        return message.get_obj() 

    # given an email it returns the id of the user associated to that email
    def email_to_id(self, email):
        return db.session.query(User).filter(User.email == email).first().id


    def create_new_message_recipient(self, message_recipient):

        db.session.add(message_recipient)
        db.session.commit()

        return message_recipient.get_recipient_obj() # TODO json file with fields to test


    def send_bottle(self, message):
        db.session.query(Message).filter(Message.id == message.id).update({'is_sent': True})
        db.session.commit()

        return True

"""
    @celery.task(name="send_notification")
    def send_notification(sender_email, recipients_list):
        for recipient_email in recipients_list:
            print("email sent to: " + recipient_email) # TODO send email OR popup
            
        return "Notifications sent"
"""