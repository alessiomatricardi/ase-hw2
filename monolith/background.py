from os import name
import os
import re
from celery import Celery
from celery.schedules import crontab
from monolith.database import User, db, Message, Message_Recipient
import datetime
from sqlalchemy.orm import aliased
from monolith.emails import send_email
import random

_APP = None
MIN_LOTTERY_POINTS = 1
MAX_LOTTERY_POINTS = 5

if os.environ.get('DOCKER_IN_USE') is not None:
    BACKEND = BROKER = 'redis://redis:6379'
else:
    BACKEND = BROKER = 'redis://localhost:6379'

celery = Celery(__name__, backend=BACKEND, broker=BROKER) # include these files in the tasks of celery

celery.conf.timezone = 'Europe/Rome' # set timezone to Rome # 'UTC'



# 
# 1st task: definition of a periodic task that checks if the lottery needs to be performed.
# for simplicity, the lottery is performed on the 15th of every month for each users, independently from the registration date
# 
# 2nd task: definition of a periodic task that checks if there are messages that need to be sent to a recipient.
# it also manage the sending of a notification in case the messages has been sent
#
celery.conf.beat_schedule = {
    'lottery_notification': {
        'task': 'lottery_notification',   
        'schedule':  crontab(0, 0, day_of_month='15') # frequency of execution: each 15 of the month
    },
    'deliver_message_and_send_notification': {
        'task': 'deliver_message_and_send_notification',    # name of the task to execute
        'schedule': crontab()                               # frequency of execution (every 1 sec)
                                                            # crontab(0, 0, day_of_month='15') --> execcute on the 15th day of the month
    },
}


@celery.task(name="lottery_notification")
def lottery_notification():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP
    
    with app.app_context():
        users = User.query.with_entities(User.id, User.email, User.firstname, User.lottery_points).all() # TODO add User.lottery_points
        for user in users: # users = [(id1, email1, firstname1), (id2, email2, firstname2), ...]
            
            recipient_id, recipient_email, recipient_firstname, recipient_lottery_points = user

            lottery_points = random.randint(MIN_LOTTERY_POINTS, MAX_LOTTERY_POINTS)

            message = f'Subject: Monthly lottery prize\n\nHi {recipient_firstname}! You won {lottery_points} points in the lottery.'
            send_email(recipient_email, message)

            recipient_lottery_points += lottery_points
            # Query to the db to update the total points of a user
            db.session.query(User).filter(User.id == recipient_id).update({'lottery_points': recipient_lottery_points})
            
        db.session.commit()


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
                sender_firstname = msg[1]
                sender_lastname = msg[2]
                recipient_email = msg[3]
                
                message = f'Subject: You received a new message!\n\n{sender_firstname} {sender_lastname} has sent you a message.'
                send_email(recipient_email, message)
                
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