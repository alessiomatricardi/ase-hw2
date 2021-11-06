from celery.utils.functional import first
from flask import Blueprint, redirect, render_template, request, abort
from flask.globals import current_app
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.expression import false

from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import UserForm, MessageForm
from flask_login import current_user
from monolith.bottlebox_logic import BottleBoxLogic
from sqlalchemy.sql import or_,and_
from monolith.emails import send_email
from monolith.message_logic import MessageLogic
from flask.helpers import flash
from werkzeug.utils import secure_filename

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

@bottlebox.route('/bottlebox/drafts', methods=['GET'])
def show_drafts():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    msg = bottlebox_logic.retrieving_messages(current_user.id,4)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Drafts')



@bottlebox.route('/message/<label>/<id>', methods=['GET', 'POST'])
def delivered_detail(label, id):
    # if <id> is not a number, render 404 page
    try:
        int(id)
    except:
        abort(404)
    
    if label != 'received' and label != 'delivered' and label != 'pending' and label != 'draft':
        abort(404)

    if label != 'draft' and request.method == 'POST':
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

            
            # check if is_read == False. If so, set it to True and send notification to sender
            if message_recipient[0].is_read == False:
                db.session.query(Message_Recipient).where(and_(Message_Recipient.id == id,Message_Recipient.recipient_id == current_user.id)).update({'is_read': True})
                db.session.commit()
                msg = "Subject: Message notification\n\nThe message you sent to " + current_user.firstname + " has been read."
                message_sender_id = db.session.query(Message).filter(Message.id == id).first().sender_id
                email = db.session.query(User).filter(User.id == message_sender_id).first().email
                send_email(email, msg)

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
        
        # case label is draft
        elif label == 'draft': 
            
            msg_logic = MessageLogic()
            if request.method == 'GET':
                form = MessageForm()
                form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id) 

                # retrieving the message
                detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == False)
                detailed_message = [ob for ob in detailed_message]
                if not detailed_message:
                    abort(404)

                detailed_message = detailed_message[0]

                recipients = []
                recipients_id = []
                recipients_emails = []
                # checking if the current user is the sender, retrieving recipients of draft
                if detailed_message.sender_id == current_user.id:
                
                    recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
                    recipients_id = [ob.recipient_id for ob in recipients_id]
                    recipients = User.query.filter(User.id.in_(recipients_id))
                    recipients = [ob for ob in recipients]

                else:
                    abort(404)

                for recipient in recipients:
                    blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                    and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == recipient.id),
                                                                    and_(Blacklist.blocked_user_id == recipient.id, Blacklist.blocking_user_id == current_user.id)
                                                                ))
                    blacklist_istance = [ob for ob in blacklist_istance]
                    if len(blacklist_istance) > 0 or not recipient.is_active:
                        flash("The user " + str(recipient.email) + " is no longer avaiable")
                        db.session.query(Message_Recipient).where(and_(Message_Recipient.id == detailed_message.id,Message_Recipient.recipient_id == recipient.id)).delete()
                        db.session.commit()
                    else:
                        recipients_emails.append(recipient.email)

                deliver_time = detailed_message.deliver_time.strftime("%Y-%m-%dT%H:%M")
                return render_template("modify_draft.html", form = form, recipients_emails = recipients_emails, content = detailed_message.content, deliver_time = deliver_time, attached = detailed_message.image, message_id = detailed_message.id)

            # else POST method
            else: 
                # handle send and modify activity
                form = request.form
                # retrieving the message
                detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == False)
                detailed_message = [ob for ob in detailed_message]
                if not detailed_message:
                    abort(404)

                detailed_message = detailed_message[0]

                recipients = []
                recipients_id = []
                recipients_emails = []
                # checking if the current user is the sender, retrieving recipients of draft
                if not detailed_message.sender_id == current_user.id:
                    abort(404)
             
                if form['submit'] == 'Delete draft': # if it is a draft, the is_sent flag will not be set to True
                    db.session.query(Message_Recipient).where(Message_Recipient.id == detailed_message.id).delete()
                    if detailed_message.image != '':
                        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', str(detailed_message.id))
                        myfile = os.path.join(directory, detailed_message.image)
                        if os.path.isfile(myfile):
                            os.remove(myfile)
                            os.rmdir(directory)
                    db.session.query(Message).where(Message.id == detailed_message.id).delete()
                    db.session.commit()
                    return render_template("index.html")

                # here it's either send or save draft
                # checking if there's new recipients for the draft
                for recipient_email in form.getlist('recipients'):
                    recipient_id = msg_logic.email_to_id(recipient_email)
                    message_recipient = db.session.query(Message_Recipient).where(Message_Recipient.id == detailed_message.id).where(Message_Recipient.recipient_id == recipient_id).all()
                    if len(message_recipient) == 0:
                        message_recipient = Message_Recipient()
                        message_recipient.id = detailed_message.id
                        message_recipient.recipient_id = recipient_id
                        db.session.add(message_recipient)
                        db.session.commit()

                db.session.query(Message).where(Message.id == detailed_message.id).update({"content": form['content']})
                db.session.query(Message).where(Message.id == detailed_message.id).update({"deliver_time": datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')})
                # checking if there is an attached image in the draft
                if request.files and request.files['attach_image'].filename != '':
                    # checking if there's a previous attached image, if so we delete it
                    if detailed_message.image != '':
                        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', str(detailed_message.id))
                        myfile = os.path.join(directory, detailed_message.image)
                        if os.path.isfile(myfile):
                            os.remove(myfile)
                    
                    file = request.files['attach_image']
                    if msg_logic.control_file(file): # proper controls on the given file

                        db.session.query(Message).where(Message.id == detailed_message.id).update({"image": secure_filename(file.filename)})
                        #detailedmessage.image = secure_filename(file.filename)
                        id = detailed_message.id

                        # TODO trycatch
                        attached_dir = os.path.join(os.getcwd(),'monolith','static','attached')
                        if not os.path.exists(attached_dir):
                            os.makedirs(attached_dir)

                        if not os.path.exists(os.path.join(attached_dir, str(id))):
                            # TODO try catch
                            os.mkdir(os.path.join(os.getcwd(),'monolith','static','attached',str(id)))

                        file.save(os.path.join(os.getcwd(),'monolith','static','attached',str(id),secure_filename(file.filename)))

                    else:
                        flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                        return redirect('/message/draft/' + str(detailed_message.id))

                if form['submit'] == 'Send bottle':
                    db.session.query(Message).where(Message.id == detailed_message.id).update({"is_sent": 1})
                
                db.session.commit()
                # if form['submit'] == 'Send bottle': # if it is a draft, the is_sent flag will not be set to True
                #     msg_logic.send_bottle(message) 

                return render_template("index.html")

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

        return render_template('/message_detail.html', message = detailed_message, sender_name = sender_name, sender_email = sender.email, blocked = blocked, recipients = blocked_info, label = label)
        #return render_template('/delivered_detail.html', message = detailed_message, sender_name = sender_name)

    else:
        # there is no logged user, redirect to login
        return redirect('/login')
