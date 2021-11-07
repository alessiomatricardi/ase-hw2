# this class contains all the logic required to handle messages
from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
import datetime
from .background import celery  
from monolith.list_logic import ListLogic
from sqlalchemy import func
import os
import shutil

# state how many points are required to delete a (sent) message
DELETING_MESSAGE_COST = 10

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

        #
        # TODO implement asynchronous sending of message at a given datetime
        #
        
        return True # TODO decide the return value depending on tests 

    # utility to chek if a user has the right to forward a message
    def is_my_message(self, user_id, msg_id):

        today = datetime.datetime.now()

        # return a void list if the user has no right on message <msg_id>
        # return a list containg the right message if the user has rights on message <msg_id>
        # you can check if the user has right on <msg_id> if the retrieved list is not empty

        messages = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id)\
                                .where(Message.is_sent == True)\
                                .where(Message.is_delivered == True)\
                                .where(Message.deliver_time <= today)\
                                .where(Message_Recipient.recipient_id == user_id)\
                                .where(Message.id == msg_id).all()
        
        return messages

    def control_file(self, file):
        if file and file.filename != '' and file.filename.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF']:
            return True
        else:
            return False

    def control_rights_on_image(self, msg_id, user_id):
        
        messages_sent = db.session.query(Message).filter(Message.sender_id == user_id).where(Message.id == msg_id).all()
        messages_received = db.session.query(Message_Recipient).filter(Message_Recipient.recipient_id == user_id).where(Message_Recipient.id==msg_id).all()
        #Message.query.join(Message_Recipient, Message.id == Message_Recipient.id).filter(Message_Recipient.recipient_id == user_id).where(Message_Recipient.id == msg_id).all()
 
        #print(messages_sent)
        #print(messages_received)
        
        if messages_sent or messages_received:
            return True
        return False

    def delete_message(self, message_to_delete):
        # check that the user has enough lottery points
        lottery_points = db.session.query(User).filter(User.id == message_to_delete.sender_id).first().lottery_points

        if lottery_points < DELETING_MESSAGE_COST:
            return False # Not enough points to delete a message
        
        # decrement lottery points
        lottery_points = lottery_points - DELETING_MESSAGE_COST
        db.session.query(User).filter(User.id == message_to_delete.sender_id).update({'lottery_points': lottery_points})

        # deleting instances of recipients
        db.session.query(Message_Recipient).where(Message_Recipient.id == message_to_delete.id).delete()

        # deleting previously attached image, if it exists
        if message_to_delete.image != '':
            
            # directory to the folder in which is stored the image
            directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', str(message_to_delete.id))
            shutil.rmtree(directory, ignore_errors=True) # remove the directory and its content

        # deleting the draft from database and committing all changes
        db.session.query(Message).where(Message.id == message_to_delete.id).delete()
        db.session.commit()

        return True # Message successfully deleted
