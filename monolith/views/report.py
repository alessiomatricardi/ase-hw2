from flask import Blueprint, render_template, redirect, abort
import datetime
from flask.globals import request
from flask_login import current_user
from monolith.database import Message, Message_Recipient, db, Report
report = Blueprint('report', __name__)

@report.route('/report',methods=['POST'])
def report_user():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        message_id = 0
        try:
            # retrieve message id from the form
            message_id = request.form['message_id']      
        except:
            abort(500) # internal server error

        # check if current user is a recipient of the message with id == message_id
        query = db.session.query(Message_Recipient).where(Message_Recipient.recipient_id == current_user.id)\
                                                   .where(Message_Recipient.id == message_id)\
                                                   .where(Message_Recipient.is_hide == False).all()
        
        if not query:
            abort(403) # the user can't do this action
        
        report_to_add = Report()
        report_to_add.message_id = message_id
        report_to_add.reporting_user_id = current_user.id
        report_to_add.report_time = datetime.datetime.now()

        try:
            db.session.add(report_to_add)
            db.session.commit()
        except:
            # this message has been already reported by this user
            abort(409)

        return redirect('/messages/received/' + str(message_id))

    else:
        abort(401) # user should login