from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import UserForm
from flask_login import current_user

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
    today = datetime.datetime.today()
    all_users = db.session.query(User).where(User.is_admin == False)
    msg = db.session.query(Message).where(Message.sender_id == current_user.id).where(Message.is_sent == True).where(Message.is_delivered == False).where(Message.deliver_time > today)

    return render_template('bottlebox.html', messages = msg, users = all_users)


@bottlebox.route('/bottlebox/received', methods=['GET'])
def show_received():
    today = datetime.datetime.today()
    all_users = db.session.query(User).where(User.is_admin == False)
    msg = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id).where(Message_Recipient.recipient_id == current_user.id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)

    return render_template('bottlebox.html', messages = msg, users = all_users)


@bottlebox.route('/bottlebox/delivered', methods=['GET'])
def show_delivered():
    today = datetime.datetime.today()
    all_users = db.session.query(User).where(User.is_admin == False)
    msg = db.session.query(Message).where(Message.sender_id == current_user.id).where(Message.is_sent == True).where(Message.is_delivered == True).where(Message.deliver_time <= today)

    return render_template('bottlebox.html', messages = msg, users = all_users)


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
            
# @bottlebox.route('/test_message')
# def create_message():
#     new_message = Message()
#     new_message.sender_id = 2
#     new_message.content = "Multiple Ciao user1 arrivederci"
#     d = datetime.date(2019, 4, 13)
#     new_message.deliver_time = d 
#     new_message.is_sent = True

#     db.session.add(new_message)
#     db.session.commit()

#     new_message_recipient1 = Message_Recipient()
#     new_message_recipient1.id = new_message.id
#     new_message_recipient1.recipient_id = 4
#     new_message_recipient1.is_read = False
#     new_message_recipient1.read_time = None

#     db.session.add(new_message_recipient1)
#     db.session.commit()

#     new_message_recipient2 = Message_Recipient()
#     new_message_recipient2.id = new_message.id
#     new_message_recipient2.recipient_id = 3
#     new_message_recipient2.is_read = False
#     new_message_recipient2.read_time = None

#     db.session.add(new_message_recipient2)
#     db.session.commit()

#     return redirect('/bottlebox?value=Delivered')

