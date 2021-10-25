# this class contains all the logic required to handle messages
from monolith.database import db, Message, Message_Recipient

# TODO import the db methods

class Message_logic:
    
    def __init__(self):
        pass

    # verifies that the message fields are consistent
    def validate_message_fields(self, message):
        return message.sender_id >= 0 # TODO and message.content not in badwords
    

    # questo metodo ritorna un oggetto json contenente l'id del messaggio creato + 
    # recipient(s) + il contenuto. 
    # Non serve qui ma per il testing
    def create_new_message(self, message):
        
        db.session.add(message)
        db.session.commit()

        return message.get_id() # TODO json file con i campi da testare
        # ritorna l'id del messaggio salvato sul db


    def create_new_message_recipient(self, message_recipient):

        db.session.add(message_recipient)
        db.session.commit()

        return message_recipient.get_recipient_id() # TODO json file con i campi da testare
