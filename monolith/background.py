from os import name
import re
from celery import Celery
from celery.schedules import crontab
from monolith.database import User, db, Message, Message_Recipient
import datetime
from sqlalchemy.orm import aliased

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER,
                include=['monolith.tasks.new_message_tasks', 'monolith.message_logic']) # include these files in the tasks of celery

celery.conf.timezone = 'Europe/Rome' # set timezone to Rome

# definition of a periodic task that checks if there are messages that need to be sent to a recipient.
# it also manage the sending of a notification in case the messages has been sent
celery.conf.beat_schedule = {
    'deliver_message_and_send_notification': {
        'task': 'deliver_message_and_send_notification',    # name of the task to execute
        'schedule': crontab()                               # frequency of execution (every 1 sec)
                                                            # crontab(0, 0, day_of_month='15') --> execcute on the 15th day of the month
    },
}

_APP = None

@celery.task(name="deliver_message_and_send_notification")
def deliver_message_and_send_notification():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP
    
    with app.app_context():
        sender = aliased(User) # alias used fro the following query
        recipient = aliased(User) # alias used fro the following query
        # the query retrieves the messages that need to be delivered and notified together with the 
        # sender firstname, lastname and the email of the recipient
        messages = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id)\
                                .where(Message.is_sent == True).where(Message.is_delivered == False)\
                                .where(Message.deliver_time < datetime.datetime.now())\
                                .join(sender, sender.id == Message.sender_id).add_columns(sender.firstname, sender.lastname)\
                                .join(recipient, recipient.id == Message_Recipient.recipient_id).add_columns(recipient.email).all()
        
        if len(messages) == 0: # no messages requires notification
            return "No notifications have to be sent"
        else: # there is at least 1 message to be notified and updated
            for msg in messages: # msg = (<Message id>, sender_firstaname, sender_lastname, recipient_email)
                # creation and sending of an email (= notification) which is sent to the recipient
                print(msg[3] + ": " + msg[1] + " " + msg[2] + " sent you a message") # TODO send an email to each recipient
                
                # the message is set as delivered in the database
                db.session.query(Message).filter(Message.id == msg[0].id).update({'is_delivered': True}) # sent the message as delivered
            
            # update the values in the database
            db.session.commit()
            return "Messages and corresponding notification sent!"


"""
_APP = None

@celery.task(name="deliver_message")
def deliver_message():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP


    return []
"""