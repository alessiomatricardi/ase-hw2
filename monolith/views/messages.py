from flask import Blueprint, redirect, render_template, request
from monolith.database import Message, db
from monolith.forms import MessageForm

messages = Blueprint('messages', __name__)


@messages.route('/new_message', methods=['POST', 'GET'])
def new_message():

    #
    # TODO verify that the user is logged in
    #

    form = MessageForm()
    
    if request.method == 'GET': # the user clicks the "new message" in the homepage
        return render_template('new_message.html', form=form) 
        #
        # TODO solve an error in rendering the new_message.html page
        #

    elif request.method == 'POST': # the user submits the form to create the new message ("Insert into a bottle" option)
        if form.validate_on_submit():
            message = Message()

            #
            # TODO
            # 1. add the message information into "message" variable
            # 2. save the message in the db
            # 3. redirect to the "CLOSE THE BOTTLE" page
            # 

            # recipient, content = form.data['recipient'], form.data['content']
          

            # TEMPLATE TAKEN FROM AUTH.PY
            #new_user = User()
            #form.populate_obj(new_user)
            #new_user.set_password(form.password.data)
            #db.session.add(new_user)
            #db.session.commit()
            #return redirect('/users')
    
    else:
        raise RuntimeError('This should not happen!')