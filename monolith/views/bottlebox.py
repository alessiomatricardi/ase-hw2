from flask import Blueprint, redirect, render_template, request, abort
from flask.globals import current_app
from sqlalchemy.sql.elements import Null
from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import HideForm, ReportForm
from flask_login import current_user
from monolith.bottlebox_logic import BottleBoxLogic
from sqlalchemy.sql import or_,and_

import datetime
import os


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

@bottlebox.route('/message/<label>/<id>', methods=['GET'])
def delivered_detail(label, id):
    # if <id> is not a number, render 404 page
    try:
        int(id)
    except:
        abort(404)
    
    if label != 'received' and label != 'delivered' and label != 'pending':
        abort(404)


    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
 
        recipients = None
        blocked_info = []
        detailed_message = None
        blocked = None

        # checking the value of the label
        if label == 'received':

            # checkig if the current_user is into recipients of the message
            message_recipient = db.session.query(Message_Recipient).where(and_(Message_Recipient.id == id,Message_Recipient.recipient_id == current_user.id))
            message_recipient = [ob for ob in message_recipient]
            if not message_recipient:
                abort(404)

            detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)
            detailed_message = [ob for ob in detailed_message]
            if not detailed_message:
                abort(404)
        
            detailed_message = detailed_message[0]

            other_id = detailed_message.sender_id

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
        

        else: # case label is pending or delivered

            detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)
            detailed_message = [ob for ob in detailed_message]
            if not detailed_message:
                abort(404)

            detailed_message = detailed_message[0]

            # checking if the current user is the sender
            if detailed_message.sender_id == current_user.id:
                
                received_message = False
                recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
                recipients_id = [ob.recipient_id for ob in recipients_id]
                recipients = User.query.filter(User.id.in_(recipients_id))
                recipients = [ob for ob in recipients]

            else:
                abort(404)
            
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

        sender = User.query.where(User.id == detailed_message.sender_id)[0]
        sender_name = sender.firstname + ' ' + sender.lastname 

        reportForm = ReportForm(message_id = id)
        hideForm = HideForm(message_id = id)

        return render_template('/message_detail.html', hideForm = hideForm, reportForm = reportForm, message = detailed_message, sender_name = sender_name, sender_email = sender.email, blocked = blocked, recipients = blocked_info, label = label)
        #return render_template('/delivered_detail.html', message = detailed_message, sender_name = sender_name)

    else:
        # there is no logged user, redirect to login
        return redirect('/login')
