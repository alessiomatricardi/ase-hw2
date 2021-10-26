from flask import Blueprint, redirect, render_template, request, json
from flask.helpers import flash, url_for
from flask.signals import request_finished
from sqlalchemy.sql.elements import Null
from monolith.database import Message, Message_Recipient, db
from monolith.forms import MessageForm
import datetime

from monolith.auth import current_user

from monolith.message_logic import Message_logic # gestisce la logica dei messaggi. 
                                                 # Ad esempio, la creazione di un nuovo messaggio + 
                                                 # richiesta al db + ritorna oggetto json per fare il test

messages = Blueprint('messages', __name__)


@messages.route('/new_message', methods=['POST', 'GET'])
def new_message():
    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):

        msg_logic = Message_logic() 

        # the user clicks the "new message" in the homepage
        if request.method == 'GET': 
            form = MessageForm()
            form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id)
            return render_template('new_message.html', form=form)

        # the user submits the form to create the new message ("Send bottle" option)
        elif request.method == 'POST': 
            
            form = request.form

            # take message content from form
            message = Message()
            message.sender_id = current_user.id
            message.content = form['content']
            message.is_sent = False # redundant because the db automatically set it to False
            message.deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M') # !!! DO NOT TOUCH !!!

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
                
                # if form['submit'] == 'Save draft' it will only redirect
                return redirect("/") 

            else:
                #msg = json.dumps({"msg":"Condition failed on page baz"})
                #db.session['msg'] = msg
                #return redirect(url_for('.do_foo', messages=messages))
                flash("Please select at least 1 reecipient")
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
