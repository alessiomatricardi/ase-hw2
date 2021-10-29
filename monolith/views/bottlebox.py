from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import UserForm
from flask_login import current_user
from monolith.bottlebox_logic import BottleBoxLogic

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

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        message = db.session.query(Message_Recipient).where(Message_Recipient.id == id).where(Message_Recipient.recipient_id == current_user.id)
        if message is not None:
            detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)[0]
            sender = User.query.where(User.id == detailed_message.sender_id)[0]
            sender_name = sender.firstname + ' ' + sender.lastname
            return render_template('/message_detail.html', message = detailed_message, sender_name = sender_name)
        else:
            # 404 TODO
            render_template('/index.html')
    else:
        # there is no logged user, redirect to login
        return redirect('/login')
