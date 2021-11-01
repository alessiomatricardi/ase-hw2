from flask import Blueprint, redirect, render_template, request, json
from flask.helpers import flash, url_for
from flask.signals import message_flashed, request_finished
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import Null
from monolith.database import Message, Message_Recipient, User, db
from monolith.forms import MessageForm
import datetime

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
            message.is_sent = False # redundant because the db automatically set it to False
            message.deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M') # !!! DO NOT TOUCH !!!
            
            # TODO add a mechanism to attach, send and handle images/documents. 
            # add a field in which store images/documents.
            # add a mechanism to render images/documents in web pages.

            # validate message content
            if msg_logic.validate_message_fields(message):
                # add message in the db
                id = msg_logic.create_new_message(message)
            else:
                # TODO handle incorrect message fields
                return render_template('/error_page.html')
            
            if len(form.getlist('recipients')) > 0: # if no recipients have been selected
                for recipient_email in form.getlist('recipients'): # list of selected recipients emails
                    message_recipient = Message_Recipient()

                    recipient_id = msg_logic.email_to_id(recipient_email)

                    # initialize the Message_Recipient object
                    message_recipient.id = id 
                    message_recipient.is_read = False # redundant because the db automatically set it to False
                    message_recipient.read_time = datetime.datetime(2020, 10, 6) # TODO it should be better to set a null vallue, but if done an error occurr
                    message_recipient.recipient_id = recipient_id
                    msg_logic.create_new_message_recipient(message_recipient)

                if form['submit'] == 'Send bottle': 
                    msg_logic.send_bottle(message) 
                    seconds = (message.deliver_time - datetime.datetime.now()).total_seconds() 
                    msg_logic.send_notification.apply_async(countdown=seconds, kwargs={'sender_email': current_user.email, 'recipients_list': form.getlist('recipients')})
                
                return redirect("/") 

            else:
                #msg = json.dumps({"msg":"Condition failed on page baz"})
                #db.session['msg'] = msg
                #return redirect(url_for('.do_foo', messages=messages))
                flash("Please select at least 1 recipient")
                return redirect(url_for('.new_message'))

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



# implement the forward_message 
# by checking if the current_user 
# has the rights to perform this
# action using the passed message
@messages.route('/new_message/<msg_id>', methods=['GET'])
def forward_message(msg_id):
    try:
        int(msg_id)
    except:
        # TODO 404
        return render_template('/index.html')


    if current_user is not None and hasattr(current_user, 'id'):

        # this is the check on the rights of the user on a given message
        msg_logic = MessageLogic()

        msg = msg_logic.is_my_message(current_user.id, msg_id)


        if msg: # the list is not empty

            # text builder
            sender = db.session.query(User).where(User.id == msg[0].sender_id)[0]
            recipient = db.session.query(User).where(User.id == current_user.id)[0]
            forward = "Sent by " + sender.firstname + " " + sender.lastname + "\nto " + recipient.firstname + " " + recipient.lastname + "\non " + str(msg[0].deliver_time) + "\n\n\n\"" + msg[0].content + "\"\n"
            ##### 

            # form builder
            form = MessageForm()
            form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id) 
            form.content.data = forward
            single_recipient = request.args.get('single_recipient') # used to set a checkbox as checked if the recipient is choosen from the recipient list page
            #####

            return render_template('new_message.html', form=form, single_recipient=single_recipient)

        else: # the list is empty so the user doesn't have any right on the selected message

            return render_template('error.html')


    else: # user not logged
        return redirect('/login') # TODO print an error
