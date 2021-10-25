from flask import Blueprint, redirect, render_template, request
from flask.signals import request_finished
from sqlalchemy.sql.elements import Null
from monolith.database import Message, Message_Recipient, db
from monolith.forms import MessageForm, BottleForm
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

        if request.method == 'GET': # the user clicks the "new message" in the homepage
            form = MessageForm()
            return render_template('new_message.html', form=form) 

        elif request.method == 'POST': # the user submits the form to create the new message ("Insert into a bottle" option)
            
            form = request.form

            message = Message()
            message.sender_id = current_user.id
            message.content = form['content']
            message.is_sent = False # redundant because the db automatically set it to False
            message.deliver_time = datetime.datetime(2020, 10, 5)

            msg_logic = Message_logic() 
            
            if msg_logic.validate_message_fields(message):
                id = msg_logic.create_new_message(message)
            else:
                # TODO handle incorrect message fields
                return render_template('/error_page.html')
            
            for recipient_id in form.getlist('recipients'): # list of selected recipients
                message_recipient = Message_Recipient()

                # initialize the Message_Recipient object
                message_recipient.id = id 
                message_recipient.is_read = False # redundant because the db automatically set it to False
                message_recipient.read_time = datetime.datetime(2020, 10, 6)
                message_recipient.recipient_id = int(recipient_id)
                msg_logic.create_new_message_recipient(message_recipient)

            # depending on what button is clicked, the rendered page will be different
            if form['submit'] == 'Insert into a bottle': 
                return redirect('/send_bottle')
            elif form['submit'] == 'Save draft':
                return redirect("/") 

            """
            TEST
            import unittest
            import monolith.Message_logic as m
            class TestAdd(unittest.TestCase):
                def test_NAME(self):
                    result = m.new_message(message)
                    self.assertEqual(result, {message_id: 1})
            """

        else:
            raise RuntimeError('This should not happen!')

    else: # user not logged
        return redirect('/login') # TODO print an error


@messages.route('/send_bottle', methods=['POST', 'GET'])
def send_bottle():
    # verify that the user is logged in
    if current_user is not None and hasattr(current_user, 'id'):
        
        if request.method == 'GET': # the user has clicked on the "Insert into a bottle" button
            form = BottleForm()
            return render_template('send_bottle.html', form=form) 

        elif request.method == 'POST': # the user submits the form to create the new message ("Insert into a bottle" option)
            
            form = request.form
            return "MESSAGE SENT"

    else: # user not logged
        return redirect('/login') # TODO print an error
