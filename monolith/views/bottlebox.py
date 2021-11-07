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
    # retrieving all pending messages(type:1) sent by current_user
    msg = bottlebox_logic.retrieving_messages(current_user.id,1)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Pending')


@bottlebox.route('/bottlebox/received', methods=['GET'])
def show_received():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    # retrieving all received messages(type:2)
    msg = bottlebox_logic.retrieving_messages(current_user.id,2)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Received')

@bottlebox.route('/bottlebox/delivered', methods=['GET'])
def show_delivered():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    # retrieving all delivered messages(type:3) sent by current_user
    msg = bottlebox_logic.retrieving_messages(current_user.id,3)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Delivered')

@bottlebox.route('/bottlebox/drafts', methods=['GET'])
def show_drafts():

    bottlebox_logic = BottleBoxLogic()

    all_users = bottlebox_logic.retrieving_all_users()
    # retrieving all drafts(type:4) stored by current_user
    msg = bottlebox_logic.retrieving_messages(current_user.id,4)

    return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Drafts')



@bottlebox.route('/message/<label>/<id>', methods=['GET', 'POST'])
def delivered_detail(label, id):

    # checks if <id> is not a number, otherwise abort
    try:
        int(id)
    except:
        abort(404)

    # checks the correctness of label variable
    if label != 'received' and label != 'delivered' and label != 'pending' and label != 'draft':
        abort(404)

    # POST method is only allowed for drafts, being possible to modify or send them 
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

            detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)
            detailed_message = [ob for ob in detailed_message]

            # checking that the <id> message exists
            if not detailed_message:
                abort(404)
        
            detailed_message = detailed_message[0]

            # checking if the current_user is into recipients of the message
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


            other_id = detailed_message.sender_id

            # checking if the message is from a blocked or blocking user 
            blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                        and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == other_id),
                                                                        and_(Blacklist.blocked_user_id == other_id, Blacklist.blocking_user_id == current_user.id)
                                                                    ))
            blacklist_istance = [ob for ob in blacklist_istance]
            
            # blocked variable is passed to render_template in order to display or not the reply and block buttons
            if not blacklist_istance:
                blocked = False
            else:
                blocked = True
        
        # case label is draft
        elif label == 'draft': 
            
            msg_logic = MessageLogic()

            # rendering the draft detail
            if request.method == 'GET':
                form = MessageForm()
                form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id) 

                # retrieving the message, if exists
                detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == False)
                detailed_message = [ob for ob in detailed_message]
                if not detailed_message:
                    abort(404)

                detailed_message = detailed_message[0]

                recipients = []
                recipients_id = []
                recipients_emails = []

                # checking if the current user is the sender, then retrieving recipients of draft
                if detailed_message.sender_id == current_user.id:
                    recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
                    recipients_id = [ob.recipient_id for ob in recipients_id]
                    recipients = User.query.filter(User.id.in_(recipients_id))
                    recipients = [ob for ob in recipients]
                else:
                    abort(404)

                # checking that already saved recipients are still available (they could have become inactive or blocked/blocking user)
                for recipient in recipients:
                    blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                    and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == recipient.id),
                                                                    and_(Blacklist.blocked_user_id == recipient.id, Blacklist.blocking_user_id == current_user.id)
                                                                ))
                    blacklist_istance = [ob for ob in blacklist_istance]
                    if len(blacklist_istance) > 0 or not recipient.is_active:
                        # the user is no longer available to receive messages from current_user either being inactive or being blocked/blocking
                        flash("The user " + str(recipient.email) + " is no longer avaiable")
                        db.session.query(Message_Recipient).where(and_(Message_Recipient.id == detailed_message.id,Message_Recipient.recipient_id == recipient.id)).delete()
                        db.session.commit()
                    else:
                        # the saved recipient is still available
                        recipients_emails.append(recipient.email)

                # defining format of datetime in order to insert it in html form
                deliver_time = detailed_message.deliver_time.strftime("%Y-%m-%dT%H:%M")

                # returning the draft html page
                return render_template("modify_draft.html", form = form, recipients_emails = recipients_emails, content = detailed_message.content, deliver_time = deliver_time, attached = detailed_message.image, message_id = detailed_message.id)

            # else = Drafts POST method: deleting draft or submitting modification/send request 
            else: 
                form = request.form

                # retrieving the draft to send, modifiy or delete it
                detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == False)
                detailed_message = [ob for ob in detailed_message]
                # checks that the draft exists
                if not detailed_message:
                    abort(404)

                detailed_message = detailed_message[0]

                recipients = []
                recipients_id = []
                recipients_emails = []

                # checking if the current user is the sender of draft
                if not detailed_message.sender_id == current_user.id:
                    abort(404)
             
                # delete draft from db, eventual image in filesystem and all message_recipients instances 
                if form['submit'] == 'Delete draft': 

                    # deleting instances of recipients
                    db.session.query(Message_Recipient).where(Message_Recipient.id == detailed_message.id).delete()

                    # deleting previously attached image, if it exists
                    if detailed_message.image != '':
                        
                        # directory to the folder in which is stored the image
                        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', str(detailed_message.id))
                        myfile = os.path.join(directory, detailed_message.image)

                        # deleting image and directory
                        if os.path.isfile(myfile):
                            os.remove(myfile)
                            os.rmdir(directory)

                    # deleting the draft from database and committing all changes
                    db.session.query(Message).where(Message.id == detailed_message.id).delete()
                    db.session.commit()

                    return render_template("index.html")

                # Now form['submit'] == 'Send bottle' or 'Save Draft'

                # checking if there's new recipients for the draft
                for recipient_email in form.getlist('recipients'):
                    
                    # retrieving id of recipient
                    recipient_id = msg_logic.email_to_id(recipient_email)

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
                        db.session.commit()

                # update content of message: if the content is not changed, it'll store the same value
                db.session.query(Message).where(Message.id == detailed_message.id).update({"content": form['content']})
                # update the deliver time for the draft
                db.session.query(Message).where(Message.id == detailed_message.id).update({"deliver_time": datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')})
                
                # checking if there is a new attached image in the form 
                if request.files and request.files['attach_image'].filename != '':
                    
                    # checking if there's a previous attached image, if so we delete it
                    if detailed_message.image != '':
                        
                        # directory where is stored the attached imaged
                        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', str(detailed_message.id))
                        myfile = os.path.join(directory, detailed_message.image)
                       
                        # deleting the previously attached image
                        if os.path.isfile(myfile):
                            os.remove(myfile)
                    
                    # retrieving newly attached image
                    file = request.files['attach_image']

                    # proper controls on the given file
                    if msg_logic.control_file(file): 

                        # updating the name of attached image inside db
                        db.session.query(Message).where(Message.id == detailed_message.id).update({"image": secure_filename(file.filename)})
                        
                        id = detailed_message.id

                        # TODO trycatch
                        attached_dir = os.path.join(os.getcwd(),'monolith','static','attached')
                        
                        # creating attached folder, if it doesn't already exist
                        if not os.path.exists(attached_dir):
                            os.makedirs(attached_dir)

                        # creating attached image folder, if it doesn't already exist
                        if not os.path.exists(os.path.join(attached_dir, str(id))):
                            # TODO try catch
                            os.mkdir(os.path.join(os.getcwd(),'monolith','static','attached',str(id)))

                        # saving the attached image
                        file.save(os.path.join(os.getcwd(),'monolith','static','attached',str(id),secure_filename(file.filename)))

                    else:
                        # control on filename fails
                        flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                        return redirect('/message/draft/' + str(detailed_message.id))

                # the draft is sent and its is_sent attribute is set to 1, from now on it's no longer possible to modify it
                # in order to stop it, it'll be necessary to spend lottery points
                if form['submit'] == 'Send bottle':
                    db.session.query(Message).where(Message.id == detailed_message.id).update({"is_sent": 1})
                
                db.session.commit()

                return render_template("index.html")


        else: # case label is pending or delivered

            # checks that message exists
            detailed_message = Message.query.where(Message.id == id).where(Message.is_sent == True)
            detailed_message = [ob for ob in detailed_message]
            if not detailed_message:
                abort(404)

            detailed_message = detailed_message[0]

            # checking if the current user is the sender
            if detailed_message.sender_id == current_user.id:
                recipients_id = db.session.query(Message_Recipient).where(Message_Recipient.id == id)
                recipients_id = [ob.recipient_id for ob in recipients_id]
                recipients = User.query.filter(User.id.in_(recipients_id))
                recipients = [ob for ob in recipients]
            else:
                abort(404)
            
            other_id = None
            # checks if a recipient has blocked the current_user or has been blocked
            for i in range(len(recipients)):
                other_id = recipients[i].id
                blacklist_istance = db.session.query(Blacklist).where(or_(
                                                                    and_(Blacklist.blocked_user_id == current_user.id, Blacklist.blocking_user_id == other_id),
                                                                    and_(Blacklist.blocked_user_id == other_id, Blacklist.blocking_user_id == current_user.id)
                                                                ))
                blacklist_istance = [ob for ob in blacklist_istance]
                
                # appends to blocked_info a tuple to link the respective recipient and its blacklist status 
                if not blacklist_istance:
                    blocked_info.append([recipients[i], False])
                else:
                    blocked_info.append([recipients[i], True])

        # retrieving sender info from db
        sender = User.query.where(User.id == detailed_message.sender_id)[0]
        sender_name = sender.firstname + ' ' + sender.lastname 

        return render_template('/message_detail.html', message = detailed_message, sender_name = sender_name, sender_email = sender.email, blocked = blocked, recipients = blocked_info, label = label)

    else:
        # there is no logged user, redirect to login
        return redirect('/login')
