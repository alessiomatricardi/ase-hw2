import re
from monolith.database import db, Message, Message_Recipient, User, Blacklist
from sqlalchemy import func
import json
import datetime

# this class contains all the logic required to display a calendar of sent and received messages
class CalendatLogic:
    
    def __init__(self):
        pass

    # return the messages sent from a specific user
    def get_list_of_sent_messages(self, user_id):

        # retrieve the list of sent messages of the user with id == user_id together with the firstname, lastname and email of the recipient of the message
        list_of_messages = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id)\
                                        .filter(Message.sender_id == user_id, Message.is_sent == True)\
                                        .join(User, User.id == Message_Recipient.recipient_id)\
                                        .add_columns(User.firstname, User.lastname, User.email).all()

        # FORMAT: list_of_messages --> [(Messsage, recipient_firstname, recipient_lastname, recipient_email), (...), ...]
        
        # create a list of lists with format [[STRING_MESSAGE, STRING_DATE, Boolean], ...]
        list_of_messages = [[f'Message sent to {el[1]} {el[2]} ({el[3]})', \
                             el[0].deliver_time.strftime('%Y-%m-%dT%H:%M'),\
                             True if el[0].deliver_time.strftime('%Y-%m-%dT%H:%M') < datetime.datetime.now().strftime('%Y-%m-%dT%H:%M') else False] for el in list_of_messages]

        # create the json of the list
        list_of_messages = json.dumps(list_of_messages)
        
        return list_of_messages
        

    # return the messages received from a specific user
    def get_list_of_received_messages(self, user_id):

        # retrieve the list of received messages of the user with id == user_id together with the firstname, lastname and email of the sender of the message
        list_of_messages = Message.query.join(Message_Recipient, Message_Recipient.id == Message.id)\
                                        .filter(Message_Recipient.recipient_id == user_id, Message.is_delivered == True)\
                                        .join(User, User.id == Message.sender_id)\
                                        .add_columns(User.firstname, User.lastname, User.email).all()
                                                  
        # FORMAT: list_of_messages --> [(Messsage, sender_firstname, sender_lastname, sender_email), (...), ...]

        # create a list of lists with format [[STRING_MESSAGE, STRING_DATE, Boolean], ...]
        list_of_messages = [[f'Message received from {el[1]} {el[2]} ({el[3]})', \
                             el[0].deliver_time.strftime('%Y-%m-%dT%H:%M'), True] for el in list_of_messages]

        # create the json of the list
        list_of_messages = json.dumps(list_of_messages)
        
        return list_of_messages
