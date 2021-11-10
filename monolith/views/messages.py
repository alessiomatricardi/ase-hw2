import datetime
import os

from flask import Blueprint, config, redirect, render_template, request, json, current_app, abort
from flask.helpers import flash, send_from_directory, url_for
from flask.signals import message_flashed, request_finished
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import Null
from werkzeug.utils import secure_filename
from monolith.message_logic import MessageLogic # it manages the logic of the messages.
from monolith.database import Message, Message_Recipient, User, db
from monolith.forms import HideForm, MessageForm
from monolith.auth import current_user


messages = Blueprint('messages', __name__)

@messages.route('/messages/new', methods=['POST', 'GET'])
def _new_message():
    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        msg_logic = MessageLogic()

        # the user clicks the "New message in a bottle" in the homepage
        if request.method == 'GET':
            form = MessageForm()

            # retrieve the list of possible recipients
            form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id)

            single_recipient = request.args.get('single_recipient') # used to set a checkbox as checked if the recipient is choosen from the recipient list page
            
            msg_id = request.args.get('msg_id')
            
            if msg_id: # if a msg_id has been given as argument

                # verify that the message with id == msg_id has been received by the currently logged user
                # if so, the message will exist                
                msg = msg_logic.is_my_message(current_user.id, msg_id)

                if msg: # the list is not empty
                    # text builder
                    sender = db.session.query(User).where(User.id == msg[0].sender_id).first()
                    recipient = db.session.query(User).where(User.id == current_user.id).first() 
                    form.content.data = "Sent by " + sender.firstname + " " + sender.lastname + "\nto " + recipient.firstname + " " + recipient.lastname + "\non " + str(msg[0].deliver_time) + "\n\n\n\"" + msg[0].content + "\"\n" # fill the content with the forward message
                    

            return render_template('new_message.html', form=form, single_recipient=single_recipient)

        elif request.method == 'POST':

            form = request.form

            # take message content from the form
            message = Message()
            message.sender_id = current_user.id
            message.content = form['content']
            message.deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')
            id = message.id

            # validate message content
            msg_logic.validate_message_fields(message)
                
            # if no recipients have been selected
            if len(form.getlist('recipients')) == 0: 
                flash("Please select at least 1 recipient")
                return redirect('/messages/new')

            
            # verify that an image has been inserted
            if request.files and request.files['attach_image'].filename != '': 

                # take the image
                file = request.files['attach_image']

                # checks on the given file
                if msg_logic.validate_file(file): 
                    message.image = secure_filename(file.filename)

                    # create the message also specifying the the filename of the image
                    id = msg_logic.create_new_message(message)['id']

                    # create the directory 'attachments' if it doesn't exist
                    attachments_dir = os.path.join(os.getcwd(),'monolith','static','attachments')
                    if not os.path.exists(attachments_dir):
                        os.makedirs(attachments_dir)

                    # create a subdirectory of 'attachments' having as name the id of the message
                    os.mkdir(os.path.join(os.getcwd(),'monolith','static','attachments',str(id)))

                    # save the image in the specified path
                    file.save(os.path.join(os.getcwd(),'monolith','static','attachments',str(id),message.image))

                # incorrect file uploaded
                else:
                    flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                    return redirect('/messages/new')
            
            # if no image has been inserted, the message is created without passing the data
            # of the image and the id of the message is retrieved
            else: 
                id = msg_logic.create_new_message(message)['id']

           
            for recipient_email in form.getlist('recipients'): # list of selected recipients emails
                message_recipient = Message_Recipient()

                recipient_id = msg_logic.email_to_id(recipient_email)


                # initialize the Message_Recipient object
                message_recipient.id = id
                message_recipient.is_read = False # redundant because the db automatically set it to False
                message_recipient.recipient_id = recipient_id
                msg_logic.create_new_message_recipient(message_recipient)


            if form['submit'] == 'Send bottle': # if it is a draft, the is_sent flag will not be set to True
                msg_logic.send_bottle(message) 

                # seconds = (message.deliver_time - datetime.datetime.now()).total_seconds() 
                # msg_logic.send_notification.apply_async(countdown=seconds, kwargs={'sender_email': current_user.email, 'recipients_list': form.getlist('recipients')})
            
            return render_template("index.html") 
          
        else:
            raise RuntimeError('This should not happen!')

    else: # redirect the user to the login page
        return redirect('/login') 

# this route allow a user to hide a message
@messages.route('/hide', methods=['POST'])
def _hide_message():
    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        form = HideForm()

        if not form.validate_on_submit():
            abort(400)

        message_id = 0
        try:
            # retrieve the message id from the form
            message_id = int(form.message_id.data)
        except:
            abort(400)  # internal server error

        try:
            # check if that user is a recipient of that message
            query = db.session.query(Message_Recipient).filter(
                Message_Recipient.recipient_id == current_user.id,
                Message_Recipient.id == message_id,
                Message_Recipient.is_hide == False
                )
            if query is None:
                abort(403) # that user can't do this action

            message_recipient = query.first()
            message_recipient.is_hide = True
            db.session.commit()
        except:
            # error occurred with the database
            abort(500)

        return redirect('/bottlebox/received')
    else:
        return redirect('/login') #user should login

# show an image attached on that message
@messages.route('/messages/<msg_id>/attachments/<filename>')
def _show_attachment(msg_id, filename):

    msg_logic = MessageLogic()

    if msg_logic.control_rights_on_image(msg_id, current_user.id): 
        return send_from_directory(os.path.join(os.getcwd(),'monolith', 'static', 'attachments',str(msg_id)), filename)
    else:
        abort(403)


# sender who deletes a message not delivered
@messages.route('/messages/<id>/remove', methods=['GET'])
def _delete_message(id):

    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        # checks if <id> is not a number, otherwise abort
        try:
            int(id)
        except:
            abort(404)

        message_to_delete = db.session.query(Message).filter(Message.id == int(id)).first()
        
        # check that the message exists or the messages hasn't been sent 
        # or the message has been delivered or the message is sent by another user
        if not message_to_delete or not message_to_delete.is_sent or message_to_delete.is_delivered or message_to_delete.sender_id != current_user.id:
            abort(404)

        msg_logic = MessageLogic()

        if not msg_logic.delete_message(message_to_delete):
            flash("Not enough points to delete a message")
            return redirect(f'/messages/pending/{id}')

        return render_template("index.html")  
    
    else:
        return redirect('/login')
