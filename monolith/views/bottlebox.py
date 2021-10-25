from flask import Blueprint, redirect, render_template, request

from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import UserForm
from monolith.auth import current_user

import datetime

bottlebox = Blueprint('bottlebox', __name__)

@bottlebox.route('/bottlebox',methods=['GET'])
def retrieving_bottlebox():

    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        v = request.args.get("value")
        
        if v == "home":
            return render_template('bottlebox_home.html')
        
        today = datetime.date.today()
        all_users = db.session.query(User).where(User.is_admin == False)
        msg = []

        # retrieving the pending messages: the ones which have been set to be delivered on a future date
        if v == "Pending":
            msg = db.session.query(Message).where(Message.sender_id == current_user.id).where(Message.is_sent == True).where(Message.deliver_time > today)


        # retrieving the already received messages
        elif v == "Received":
            msg = Message.query.join(Message_Recipient, Message.id == Message_Recipient.id).where(Message_Recipient.recipient_id == current_user.id).where(Message.is_sent == True).where(Message.deliver_time <= today)

        
        # retrieving the sent and delivered messages: the ones that have been set to be delivered on a past date or on the current date
        elif v == "Delivered":
            msg = db.session.query(Message).where(Message.sender_id == current_user.id).where(Message.is_sent == True).where(Message.deliver_time <= today)


        return render_template('bottlebox.html', value = v, messages = msg, users = all_users)

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

