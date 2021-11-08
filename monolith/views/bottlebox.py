from re import I
from celery.utils.functional import first
from flask import Blueprint, redirect, render_template, request, abort
from flask.globals import current_app
from sqlalchemy.sql.elements import Null
from monolith.database import User, db, Blacklist, Message, Message_Recipient
from monolith.forms import HideForm, ReportForm, MessageForm
from flask_login import current_user
from monolith.bottlebox_logic import BottleBoxLogic, DraftLogic
from sqlalchemy.sql import or_,and_
from monolith.emails import send_email
from monolith.message_logic import MessageLogic
from flask.helpers import flash
from werkzeug.utils import secure_filename

import datetime
import os
import shutil


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
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        bottlebox_logic = BottleBoxLogic()

        all_users = bottlebox_logic.retrieving_all_users()
        # retrieving all pending messages(type:1) sent by current_user
        msg = bottlebox_logic.retrieving_messages(current_user.id,1)

        return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Pending')
    else:
        return redirect('/login')


@bottlebox.route('/bottlebox/received', methods=['GET'])
def show_received():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        bottlebox_logic = BottleBoxLogic()

        all_users = bottlebox_logic.retrieving_all_users()
        # retrieving all received messages(type:2)
        msg = bottlebox_logic.retrieving_messages(current_user.id,2)

        return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Received')

    else:
        return redirect('/login')


@bottlebox.route('/bottlebox/delivered', methods=['GET'])
def show_delivered():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):
        
        bottlebox_logic = BottleBoxLogic()

        bottlebox_logic = BottleBoxLogic()

        all_users = bottlebox_logic.retrieving_all_users()
        # retrieving all delivered messages(type:3) sent by current_user
        msg = bottlebox_logic.retrieving_messages(current_user.id,3)

        return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Delivered')
    else:
        return redirect('/login')


@bottlebox.route('/bottlebox/drafts', methods=['GET'])
def show_drafts():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        bottlebox_logic = BottleBoxLogic()

        all_users = bottlebox_logic.retrieving_all_users()
        # retrieving all drafts(type:4) stored by current_user
        msg = bottlebox_logic.retrieving_messages(current_user.id,4)

        return render_template('bottlebox.html', messages = msg, users = all_users, label = 'Drafts')

    else:
        return redirect('/login')


@bottlebox.route('/message/<label>/<id>', methods=['GET', 'POST'])
def _message_detail(label, id):

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

        bottlebox_logic = BottleBoxLogic()

        # checking the value of the label
        if label == 'received':

            detailed_message = bottlebox_logic.retrieve_received_message(id)

            # checking that the <id> message exists
            if not detailed_message:
                abort(404)

            detailed_message = detailed_message[0]

            # checking if the current_user is into recipients of the message
            message_recipient = bottlebox_logic.is_recipient(id,current_user.id)

            if not message_recipient:
                abort(404)

            # check if is_read == False. If so, set it to True and send notification to sender
            if message_recipient[0].is_read == False:

                if not bottlebox_logic.notify_on_read(id,current_user):
                    abort(500)

            other_id = detailed_message.sender_id

            # checking if the message is from a blocked or blocking user
            blacklist_istance = bottlebox_logic.user_blacklist_status(other_id,current_user.id)

            # blocked variable is passed to render_template in order to display or not the reply and block buttons
            if not blacklist_istance:
                blocked = False
            else:
                blocked = True

        # case label is draft
        elif label == 'draft':

            msg_logic = MessageLogic()
            draft_logic = DraftLogic()

            # rendering the draft detail
            if request.method == 'GET':
                form = MessageForm()
                form.recipients.choices = msg_logic.get_list_of_recipients_email(current_user.id)

                # retrieving the message, if exists
                detailed_message = draft_logic.retrieve_draft(id)
                if not detailed_message:
                    abort(404)

                detailed_message = detailed_message[0]

                recipients = []
                # recipients_id = []
                recipients_emails = []

                # checking if the current user is the sender, then retrieving recipients of draft
                if detailed_message.sender_id == current_user.id:
                    recipients = draft_logic.retrieve_current_draft_recipients(id)
                else:
                    abort(404)

                # checking that already saved recipients are still available (they could have become inactive or blocked/blocking user)
                for recipient in recipients:
                    blacklist_istance = draft_logic.recipient_blacklist_status(current_user.id,recipient.id)
                    if len(blacklist_istance) > 0 or not recipient.is_active:
                        # the user is no longer available to receive messages from current_user either being inactive or being blocked/blocking
                        flash("The user " + str(recipient.email) + " is no longer avaiable")
                        if not draft_logic.remove_unavailable_recipient(detailed_message.id,recipient.id):
                            abort(500)
                    else:
                        # the saved recipient is still available
                        recipients_emails.append(recipient.email)

                # defining format of datetime in order to insert it in html form
                deliver_time = detailed_message.deliver_time.strftime("%Y-%m-%dT%H:%M")

                # returning the draft html page
                return render_template("modify_draft.html", form = form, recipients_emails = recipients_emails, content = detailed_message.content, deliver_time = deliver_time, attachment = detailed_message.image, message_id = detailed_message.id)

            # else = Drafts POST method: deleting draft or submitting modification/send request
            else:
                form = request.form

                # retrieving the draft to send, modifiy or delete it
                detailed_message = draft_logic.retrieve_draft(id)
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

                    if not draft_logic.delete_draft(detailed_message):
                        abort(500)

                    return render_template("index.html")

                # Now form['submit'] == 'Send bottle' or 'Save Draft'

                # checking if there's new recipients for the draft
                for recipient_email in form.getlist('recipients'):

                    # retrieving id of recipient
                    recipient_id = msg_logic.email_to_id(recipient_email)

                    # add recipient to draft if not already stored
                    if not draft_logic.update_recipients(detailed_message,recipient_id):
                        abort(500)

                # update content of message: if the content is not changed, it'll store the same value
                if not draft_logic.update_content(detailed_message,form):
                    abort(500)
                # update the deliver time for the draft
                if not draft_logic.update_deliver_time(detailed_message,form):
                    abort(500)

                # checking if there is a new attached image in the form
                if request.files and request.files['attach_image'].filename != '':

                    # checking if there's a previous attached image, if so we delete it
                    if detailed_message.image != '':

                        if not draft_logic.delete_previously_attached_image(detailed_message):
                            abort(500)

                    # retrieving newly attached image
                    file = request.files['attach_image']

                    # proper controls on the given file
                    if msg_logic.validate_file(file):

                        if not draft_logic.update_attached_image(detailed_message,file):
                            abort(500)

                    else:
                        # control on filename fails
                        flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                        return redirect('/message/draft/' + str(detailed_message.id))

                # the draft is sent and its is_sent attribute is set to 1, from now on it's no longer possible to modify it
                # in order to stop it, it'll be necessary to spend lottery points
                if form['submit'] == 'Send bottle':
                    if not draft_logic.send_draft(detailed_message):
                        abort(500)

                return render_template("index.html")


        else: # case label is pending or delivered

            # checks that message exists
            if label == 'pending':
                detailed_message = bottlebox_logic.retrieve_pending_message(id)
            else:
                detailed_message = bottlebox_logic.retrieve_delivered_message(id)

            if not detailed_message:
                abort(404)

            detailed_message = detailed_message[0]

            # checking if the current user is the sender
            if detailed_message.sender_id == current_user.id:
                recipients = bottlebox_logic.retrieve_recipients(id)
            else:
                abort(404)

            other_id = None

            # checks if a recipient has blocked the current_user or has been blocked
            for i in range(len(recipients)):
                other_id = recipients[i].id

                blacklist_istance = bottlebox_logic.user_blacklist_status(other_id,current_user.id)

                # appends to blocked_info a tuple to link the respective recipient and its blacklist status
                if not blacklist_istance:
                    blocked_info.append([recipients[i], False])
                else:
                    blocked_info.append([recipients[i], True])

        # retrieving sender info from db
        sender = User.query.where(User.id == detailed_message.sender_id)[0]
        sender_name = sender.firstname + ' ' + sender.lastname
        sender_name = bottlebox_logic.retrieve_sender_info(detailed_message)

        reportForm = ReportForm(message_id = id)
        hideForm = HideForm(message_id = id)

        return render_template('/message_detail.html', hideForm = hideForm, reportForm = reportForm, message = detailed_message, sender_name = sender_name, sender_email = sender.email, blocked = blocked, recipients = blocked_info, label = label)

    else:
        # there is no logged user, redirect to login
        return redirect('/login')
