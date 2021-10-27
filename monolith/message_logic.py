# this class contains all the logic required to handle messages
from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
import datetime
from .background import celery

class MessageLogic:
    
    def __init__(self):
        pass

    # create a STRING of recipients' emails to be usedwhen sending a message
    def get_list_of_recipients_email(self, sender_id):
        list_of_recipients = db.session.query(User).filter(User.id != sender_id).all()
        #
        # TODO check if some recipient is in the black list
        # TODO merge with file of Marco/RiccardoB – KEEP ATTENTION TO THE CHECKS (e.g., user not in blacklist)
        #
        return [(recipient.email, recipient.email) for recipient in list_of_recipients]


    # verifies that the message fields are consistent
    def validate_message_fields(self, message):
        if message.deliver_time < datetime.datetime.now():#.strftime("%Y-%m-%dT%H:%M"): # check if the datetime is correct
            message.deliver_time = datetime.datetime.now() # if it set to a past day, it is sent with current datetime

        #
        # TODO and message.content not in badwords IF THE FILTER IS ACTIVE (content_filter_enabled)
        #
        return True # it could be useful for the testing phase 
                    # to return a JSON file with { message_id, recipient(s), content }
    

    # add a new message into the database
    def create_new_message(self, message):
        
        db.session.add(message)
        db.session.commit()

        return message.get_id() # TODO json file con i campi da testare
        # ritorna l'id del messaggio salvato sul db


    # given an email it returns the id of the user associated to that email
    def email_to_id(self, email):
        return db.session.query(User).filter(User.email == email).first().id


    def create_new_message_recipient(self, message_recipient):

        db.session.add(message_recipient)
        db.session.commit()

        return message_recipient.get_recipient_id() # TODO json file with fields to test


    def send_bottle(self, message):
        print(message.id)
        db.session.query(Message).filter(Message.id == message.id).update({'is_sent': True})
        db.session.commit()

        #
        # TODO implement asynchronous sending of message at a given datetime
        #
        
        return True # TODO decide the return value depending on tests 

    @celery.task(name="send_notification")
    def send_notification(sender_email, recipients_list):
        for recipient_email in recipients_list:
            print("email sent to: " + recipient_email) # TODO send email OR popup
            
        return "Notifications sent"