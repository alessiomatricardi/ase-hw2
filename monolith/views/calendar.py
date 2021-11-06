from flask import Blueprint, redirect, render_template, request, abort
from monolith.database import db, User, Message
from flask_login import current_user
from monolith.calendar_logic import CalendatLogic

calendar = Blueprint('calendar', __name__)


@calendar.route('/calendar',methods=['GET'])
def which_calendar():
    if current_user is not None and hasattr(current_user, 'id'):
        return render_template('which_calendar.html')


@calendar.route('/calendar/sent_messages',methods=['GET'])
def calendar_of_sent_messages():
    if current_user is not None and hasattr(current_user, 'id'):
        
        cl = CalendatLogic()

        # get list of sent messages converted in JSON format
        messages = cl.get_list_of_sent_messages(current_user.id)

        return render_template('calendar.html', messages=messages)


@calendar.route('/calendar/received_messages',methods=['GET'])
def calendar_of_received_messages():
    if current_user is not None and hasattr(current_user, 'id'):
        
        cl = CalendatLogic()

        # get list of received messages converted in JSON format
        messages = cl.get_list_of_received_messages(current_user.id)

        return render_template('calendar.html', messages=messages)
