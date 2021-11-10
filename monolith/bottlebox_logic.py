from sqlalchemy.sql.expression import false
from pydantic.errors import MissingError
from monolith.content_filter_logic import ContentFilterLogic
from monolith.database import Blacklist, db, Message, Message_Recipient, User, Blacklist
from sqlalchemy.sql import or_,and_
from werkzeug.utils import secure_filename
from monolith.emails import send_email

import datetime
import shutil
import os

class BottleBoxLogic:

    def __init__(self):
        pass

    #utility to retriev all the users except for the admin
    def retrieving_all_users(self):
        return db.session.query(User).where(User.is_admin == False)

    # utility to retrieve messages of the user user_id from db: type 1 for pending, type 2 for received, type 3 for delivered, type 4 for drafts
    def  retrieving_messages(self,user_id,type):
        
        user = db.session.query(User).filter(User.id == user_id).first()
        
        filter = ContentFilterLogic()

        today = datetime.datetime.now()

        if type == 1: #pending
            msg = db.session.query(Message).where(Message.sender_id == user.id).where(Message.is_sent == True).where(Message.is_delivered == False)
            
            #if the content filter is active, all the messages will be displayed censored
            if filter.filter_enabled(user.id):
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content
            
            return msg
        elif type == 2: #received
            msg = db.session.query(Message).join(Message_Recipient, Message.id == Message_Recipient.id).\
                add_columns(Message_Recipient.is_read).\
                filter(Message_Recipient.recipient_id == user.id,
                Message.is_sent == True,
                Message.is_delivered == True,
                Message_Recipient.is_hide == False).all()

            '''
            for message in msg
                message[0] -> Message object
                message[1] -> is_read boolean
            '''

            # we need to adjust this situation
            to_return = []
            for message in msg:
                message[0].is_read = message[1]
                to_return.append(message[0])

            #if the content filter is active, all the messages will be displayed censored
            if filter.filter_enabled(user.id):
                for message in to_return:
                    censored_content = filter.check_message_content(message.content)
                    message.content = censored_content
            return to_return
        elif type == 3: #delivered
            msg = db.session.query(Message).where(Message.sender_id == user.id).where(Message.is_sent == True).where(Message.is_delivered == True)
            
            #if the content filter is active, all the messages will be displayed censored
            if filter.filter_enabled(user.id):
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content

            return msg
        elif type == 4: #drafts
            msg = db.session.query(Message).where(Message.sender_id == user.id).where(Message.is_sent == False)

            #if the content filter is active, all the messages will be displayed censored
            if user.content_filter_enabled:
                for message in msg:
                   censored_content = filter.check_message_content(message.content)
                   message.content = censored_content

            return msg
        else:
            return False

    def is_recipient(self,id,current_user_id):
        message_recipient = db.session.query(Message_Recipient).where(and_(Message_Recipient.id == id,Message_Recipient.recipient_id == current_user_id))
        message_recipient = [ob for ob in message_recipient]
        return message_recipient

    def retrieve_received_message(self, id):
        detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True).where(Message.is_delivered == True)
        detailed_message = [ob for ob in detailed_message]


        return detailed_message

    #retrieves a pending message
    def retrieve_pending_message(self, id):
        detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True).where(Message.is_delivered == False)# False : pending
        detailed_message = [ob for ob in detailed_message]

        return detailed_message

    #retrieves a delivered message        
    def retrieve_delivered_message(self, id):
        detailed_message = Message.query.where(Message.id == id).where(
            Message.is_sent == True).where(Message.is_delivered == True)  # True : delivered
        detailed_message = [ob for ob in detailed_message]

        return detailed_message

    def retrieve_recipients(self, id):
        recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
        recipients_id = [ob.recipient_id for ob in recipients_id]
        recipients = User.query.filter(User.id.in_(recipients_id))
        recipients = [ob for ob in recipients]

        return recipients

    #utility to understand if the user current_user_id blocked or is blocked by the user other_id

    def user_blacklist_status(self, other_id, current_user_id):
        blacklist_instance = db.session.query(Blacklist).where(or_(
                                                            and_(Blacklist.blocked_user_id == current_user_id, Blacklist.blocking_user_id == other_id),
                                                            and_(Blacklist.blocked_user_id == other_id, Blacklist.blocking_user_id == current_user_id)
                                                        ))
        blacklist_instance = [ob for ob in blacklist_instance]

        return blacklist_instance


    #returns firstname and lastname of the user that sent the message detailed_message
    def retrieve_sender_info(self, detailed_message):
        sender = User.query.where(User.id == detailed_message.sender_id)[0]
        
        return sender.firstname + ' ' + sender.lastname

    #set the is_read flag to true in the Message_Recipient table and send an email to the sender of that message to notify that a recipient read it         
    def notify_on_read(self, id, current_user):
        db.session.query(Message_Recipient).where(and_(Message_Recipient.id == id,Message_Recipient.recipient_id == current_user.id)).update({'is_read': True})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False
        msg = "Subject: Message notification\n\nThe message you sent to " + current_user.firstname + " has been read."
        message_sender_id = db.session.query(Message).filter(Message.id == id).first().sender_id
        email = db.session.query(User).filter(User.id == message_sender_id).first().email
       
        return send_email(email, msg)


class DraftLogic:

    def __init__(self):
        pass

    def delete_draft(self, detailed_message):
        # deleting instances of recipients
        db.session.query(Message_Recipient).where(Message_Recipient.id == detailed_message.id).delete()

        # deleting previously attached image, if it exists
        if detailed_message.image != '':
            
            # directory to the folder in which is stored the image
            directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attachments', str(detailed_message.id))
            shutil.rmtree(directory, ignore_errors=True)

            '''myfile = os.path.join(directory, detailed_message.image)

            # deleting image and directory
            if os.path.isfile(myfile):
                os.remove(myfile)
                os.rmdir(directory)'''
        #retrieves a draft from its id
        # deleting the draft from database and committing all changes
        db.session.query(Message).where(Message.id == detailed_message.id).delete()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()            
            return False

        return True

    
    def retrieve_draft(self, id):
        detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == False)
        detailed_message = [ob for ob in detailed_message]
    
        return detailed_message

    #retrieves all the recipients of the message id
    def retrieve_current_draft_recipients(self, id):
        recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
        recipients_id = [ob.recipient_id for ob in recipients_id]
        recipients = User.query.filter(User.id.in_(recipients_id))
        recipients = [ob for ob in recipients]

        return recipients


    #to understand if current_user blocked or is blocked by recipient_id
    def recipient_blacklist_status(self, current_user_id, recipient_id):
        blacklist_istance = db.session.query(Blacklist).where(or_(
                                                        and_(Blacklist.blocked_user_id == current_user_id, Blacklist.blocking_user_id == recipient_id),
                                                        and_(Blacklist.blocked_user_id == recipient_id, Blacklist.blocking_user_id == current_user_id)
                                                    ))
        blacklist_istance = [ob for ob in blacklist_istance]

        return blacklist_istance


    #delete a user from the recipients of the message detailed_message_id
    def remove_unavailable_recipient(self, detailed_message_id, recipient_id):
        db.session.query(Message_Recipient).where(and_(Message_Recipient.id == detailed_message_id,Message_Recipient.recipient_id == recipient_id)).delete()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False

        return True

    def update_recipients(self, detailed_message, recipient_id):
        # retrieving eventual instance of message_recipient for current draft and recipient
        message_recipient = db.session.query(Message_Recipient).where(Message_Recipient.id == detailed_message.id).where(Message_Recipient.recipient_id == recipient_id).all()
        
        # checks if there is not instance 
        if len(message_recipient) == 0:
            
            # creates instance of new message_recipient in order to possibly send the message to the new selected recipient
            message_recipient = Message_Recipient()
            message_recipient.id = detailed_message.id
            message_recipient.recipient_id = recipient_id

            # adds row to db
            db.session.add(message_recipient)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return False

        return True


    #modify the content of a message
    def update_content(self, detailed_message, form):
        db.session.query(Message).where(Message.id == detailed_message.id).update({"content": form['content']})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False

        return True

    #modify the deliver_time of a message
    def update_deliver_time(self, detailed_message, form):
        db.session.query(Message).where(Message.id == detailed_message.id).update({"deliver_time": datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False

        return True

    def delete_previously_attached_image(self, detailed_message):
        # directory where is stored the attached imaged
        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attachments', str(detailed_message.id))
        myfile = os.path.join(directory, detailed_message.image)
        
        # deleting the previously attached image
        if os.path.isfile(myfile):
            try:
                os.remove(myfile)
            except Exception:
                return False
        
        return True


    def update_attached_image(self, detailed_message, file):

        # updating the name of attached image inside db
        db.session.query(Message).where(Message.id == detailed_message.id).update({"image": secure_filename(file.filename)})
        
        id = detailed_message.id

        attached_dir = os.path.join(os.getcwd(),'monolith','static','attachments')
        
        # creating attached folder, if it doesn't already exist
        if not os.path.exists(attached_dir):
            try:
                os.makedirs(attached_dir)
            except Exception:
                return False

        # creating attached image folder, if it doesn't already exist
        if not os.path.exists(os.path.join(attached_dir, str(id))):
            try:
                os.mkdir(os.path.join(os.getcwd(),'monolith','static','attachments',str(id)))
            except Exception:
                return False

        # saving the attached image
        try:
            file.save(os.path.join(os.getcwd(),'monolith','static','attachments',str(id),secure_filename(file.filename)))
        except Exception:
                return False

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False
        
        return True

    #send a message that was previously saved as draft
    def send_draft(self, detailed_message):
        db.session.query(Message).where(Message.id == detailed_message.id).update({"is_sent": 1})
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return False

        return True
        