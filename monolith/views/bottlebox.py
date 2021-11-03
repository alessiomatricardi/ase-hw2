from flask import Blueprint, redirect, render_template, request,abort

from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import UserForm
from flask_login import current_user
from monolith.bottlebox_logic import BottleBoxLogic
from sqlalchemy.sql import or_,and_

import datetime


bottlebox = Blueprint('bottlebox', __name__)


@bottlebox.route('/bottlebox',methods=['GET'])
def bottlebox_home():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template('bottlebox_home.html')
    else:
        # there is no logged user, redirect to login
        return redirect('/login')

@bottlebox.route('/bottlebox/pending', methods=['GET'])
def show_pending():
    
    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    msg = bottlebox_logic.retrieving_messages(current_user.id,1)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Pending')


@bottlebox.route('/bottlebox/received', methods=['GET'])
def show_received():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    msg = bottlebox_logic.retrieving_messages(current_user.id,2)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Received')


@bottlebox.route('/bottlebox/delivered', methods=['GET'])
def show_delivered():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    msg = bottlebox_logic.retrieving_messages(current_user.id,3)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Delivered')


@bottlebox.route('/message/<id>', methods=['GET'])
def message_detail(id):
    # if <id> is not a number, render 404 page
    try:
        int(id)
    except:
        # TODO 404
        return render_template('/index.html')

    received_message = True

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        # checkig if the current_user is into recipients of the message
        message = db.session.query(Message_Recipient).where(and_(Message_Recipient.id == id,Message_Recipient.recipient_id == current_user.id))
        message = [ob for ob in message]
        detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)
        detailed_message = [ob for ob in detailed_message]
        
        if not detailed_message:
            abort(404)
        
        detailed_message = detailed_message[0]

        recipients = None
        blocked_info = []
        if detailed_message.sender_id == current_user.id:
            
            received_message = False
            recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
            recipients_id = [ob.recipient_id for ob in recipients_id]
            recipients = User.query.filter(User.id.in_(recipients_id))
            recipients = [ob for ob in recipients]
            #blocked_info = []
            #print("hello world")


        if not received_message or (message != [] and detailed_message.is_delivered):
            sender = User.query.where(User.id == detailed_message.sender_id)[0]
            sender_name = sender.firstname + ' ' + sender.lastname
            
            blocked = None
            # case 1: the message is a received one, need to check if the sender is blocked or has blocked the current user
            if received_message:
                other_id = sender.id
                # checking if the message is from a blocked or blocking user 
                blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                            and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == other_id),
                                                                            and_(Blacklist.blocked_user_id == other_id, Blacklist.blocking_user_id == current_user.id)
                                                                        ))
                blacklist_istance = [ob for ob in blacklist_istance]
                
                if not blacklist_istance:
                    blocked = False
                else:
                    blocked = True
            # case 2: the message is either a pending or a delivered one, need to check every possibile recipient if they have/have been blocked
            else: 
                other_id = None
                for i in range(len(recipients)):
                    other_id = recipients[i].id
                    blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                        and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == other_id),
                                                                        and_(Blacklist.blocked_user_id == other_id, Blacklist.blocking_user_id == current_user.id)
                                                                    ))
                    blacklist_istance = [ob for ob in blacklist_istance]
                    if not blacklist_istance:
                        blocked_info.append([recipients[i], False])
                    else:
                        blocked_info.append([recipients[i], True])


            return render_template('/message_detail.html', message = detailed_message, sender_name = sender_name, sender_email = sender.email, blocked = blocked, received = received_message, recipients = blocked_info)
        else:
            # 404 TODO
            # render_template('/index.html')

            # in case of retrieving a message not sent to current_user
            abort(404,'Failure on retrieving message')
    else:
        # there is no logged user, redirect to login
        return redirect('/login')
