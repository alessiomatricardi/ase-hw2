import datetime
import os

from flask import Blueprint, config, redirect, render_template, request, json, current_app, abort
from flask.helpers import flash, send_from_directory, url_for
from flask.signals import message_flashed, request_finished
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import Null
from werkzeug.utils import secure_filename
from monolith.message_logic import MessageLogic
from monolith.database import Message, Message_Recipient, User, db
from monolith.forms import MessageForm
from monolith.auth import current_user



from monolith.message_logic import MessageLogic # gestisce la logica dei messaggi. 
                                                # Ad esempio, la creazione di un nuovo messaggio + 
                                                # richiesta al db + ritorna oggetto json per fare il test



messages = Blueprint('messages', __name__)

@messages.route('/new_message', methods=['POST', 'GET'])
def new_message():
    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        msg_logic = MessageLogic() 

        # the user clicks the "new message" in the homepage
        if request.method == 'GET': 
            form = MessageForm()
            form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id) 
            single_recipient = request.args.get('single_recipient') # used to set a checkbox as checked if the recipient is choosen from the recipient list page
            msg_id = request.args.get('msg_id')
            
            print(msg_id)
            if msg_id: # if a message id has been given as argument
                
                msg = msg_logic.is_my_message(current_user.id, msg_id)
                if msg: # the list is not empty
            
                    # text builder
                    sender = db.session.query(User).where(User.id == msg[0].sender_id)[0]
                    recipient = db.session.query(User).where(User.id == current_user.id)[0]
                    "Sent by " + sender.firstname + " " + sender.lastname + "\nto " + recipient.firstname + " " + recipient.lastname + "\non " + str(msg[0].deliver_time) + "\n\n\n\"" + msg[0].content + "\"\n"
                    form.content.data = "Sent by " + sender.firstname + " " + sender.lastname + "\nto " + recipient.firstname + " " + recipient.lastname + "\non " + str(msg[0].deliver_time) + "\n\n\n\"" + msg[0].content + "\"\n" # fill the content with the forward message
                    #####
                
            #
            # TODO add multiple_recipients in case a draft with more than 1 recipient has been saved
            #      json_var = request.get_json()
            #      multiple_recipients = json_var['NOME_DELLA_VARIABILE_JSON']
            #      
            #      pass multiple recipients into render_template
            #
            
            return render_template('new_message.html', form=form, single_recipient=single_recipient)

        # the user submits the form to create the new message ("Send bottle" option)
        elif request.method == 'POST': 
            
            form = request.form

            # take message content from form
            message = Message()
            message.sender_id = current_user.id
            message.content = form['content']
            message.deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M') # !!! DO NOT TOUCH !!!
            id = message.id

            # validate message content
            if msg_logic.validate_message_fields(message):
                
                
                # add message in the db
                if not request.files['attach_image'].filename == '': # if the user passes it, save a file in a reposistory and set the field message.image to the filename
                    
                    file = request.files['attach_image']

                    if msg_logic.control_file(file): # proper controls on the given file

                        message.image = secure_filename(file.filename)
                        id = msg_logic.create_new_message(message)['id']
                        path_to_folder = os.getcwd() + '/monolith/static/attached/' + str(id)
                        os.mkdir(path_to_folder)    
                        file.save(os.path.join(path_to_folder, message.image))

                    else:
                        flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                        return redirect('/new_message')
                
                else:
                    id = msg_logic.create_new_message(message)['id']

            else:
                # TODO handle incorrect message fields
                return render_template('/error_page.html')
            
            if len(form.getlist('recipients')) > 0: # if no recipients have been selected
                for recipient_email in form.getlist('recipients'): # list of selected recipients emails
                    message_recipient = Message_Recipient()

                    recipient_id = msg_logic.email_to_id(recipient_email)

                    # initialize the Message_Recipient object
                    message_recipient.id = id
                    print(id)
                    message_recipient.is_read = False # redundant because the db automatically set it to False
                    message_recipient.recipient_id = recipient_id
                    msg_logic.create_new_message_recipient(message_recipient)

                if form['submit'] == 'Send bottle': # if it is a draft, the is_sent flag will not be set to True
                    msg_logic.send_bottle(message) 
                
                """elif form['submit'] == 'Save draft':
                    pass"""
                    # seconds = (message.deliver_time - datetime.datetime.now()).total_seconds() 
                    # msg_logic.send_notification.apply_async(countdown=seconds, kwargs={'sender_email': current_user.email, 'recipients_list': form.getlist('recipients')})
                
                return render_template("index.html") 

            else:
                #msg = json.dumps({"msg":"Condition failed on page baz"})
                #db.session['msg'] = msg
                #return redirect(url_for('.do_foo', messages=messages))
                flash("Please select at least 1 recipient")
                #return redirect(url_for('.new_message'))
                return redirect('/new_message') # TODO VEDIAMO COSA SUCCEDE con questo

            """
            TEST
            import unittest
            import monolith.Message_logic as m
            class TestAdd(unittest.TestCase):
                def test_NAME(self):
                    # il db è vuoto
                    result = m.new_message(message)
                    self.assertEqual(result, {message_id: 1})
            """

        else:
            raise RuntimeError('This should not happen!')

    else: # user not logged
        return redirect('/login') # TODO print an error

# utility to show an image, do not change
@messages.route('/show/<msg_id>/<filename>')
def send_file(msg_id, filename):

    msg_logic = MessageLogic()

    if msg_logic.control_rights_on_image(msg_id, current_user.id): 
        return send_from_directory(os.getcwd() + '/monolith/static/attached/' + str(msg_id), filename)
    else:
        # TODO handle no suorce requested
        abort(403)

    

    
   