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
            message_id = request.form.get('message_id', type=int)        
        except:
            abort(500) # internal server error

        # check if that user is a recipient of that message
        query = db.session.query(Message_Recipient).where(Message_Recipient.recipient_id == current_user.id).where(Message.id == message_id).where(Message_Recipient.is_hide == False)
        if query is None:
            abort(403) # that user can't do this action
        
        report_to_add = Report()
        report_to_add.message_id = message_id
        report_to_add.reporting_user_id = current_user.id
        report_to_add.report_time = datetime.datetime.now()

        try:
            db.session.add(report_to_add)
            db.session.commit()
        except:
            # this message has been already reported by this user
            # this should not happen but we handle it
            abort(409)

        return redirect('/message/received/' + str(message_id) + "/")

    else:
        abort(401) # user should login