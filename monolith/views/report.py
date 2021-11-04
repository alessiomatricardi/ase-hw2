from flask import Blueprint, render_template, redirect
import datetime
from monolith.auth import current_user
from monolith.database import Message, Message_Recipient, db, Report
from monolith.forms import ReportForm
report = Blueprint('report', __name__)

@report.route('/report',methods=['POST'])
def report_user():
    # checking if there is a logged user
    if current_user is not None and hasattr(current_user, 'id'):

        form = ReportForm()

        # retrieve data from form
        message_id = form.message_id

        print(message_id + "message is")
        
        # check if that user is a recipient of that message
        query = db.session.query(Message_Recipient).where(Message_Recipient.get_recipient_id() == current_user.id).where(Message.id == message_id)
        if query is None:
            # TODO unauthorized
            return redirect('/login')
        
        print("reachedddd")
        
        report_to_add = Report()
        report_to_add.message_id = message_id
        report_to_add.reporting_user_id = current_user.id
        report_to_add.report_time = datetime.datetime.now()

        db.session.add(report_to_add)
        db.session.commit()

        redirect('/login')

        #return render_template('blacklist.html', blacklist = blacklist, users = users)
    else:
        # TODO NOT AUTHORIZED
        return redirect('/login')