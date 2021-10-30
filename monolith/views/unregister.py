from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user

from monolith.database import User, db
from monolith.forms import UnregisterForm
from monolith.auth import current_user

unregister = Blueprint('unregister', __name__)

@unregister.route('/unregister', methods = ['GET', 'POST'])
def confirmation():

    # checking if there is a logged user, otherwise redirect to login
    if current_user is not None and hasattr(current_user, 'id'):

        form = UnregisterForm()
        # using a form to verify authenticity of the unregistration request through password
        if form.validate_on_submit():
            password = form.data['password']
            q = db.session.query(User).where(User.id == current_user.id)
            user = q.first()
            # if the password is correct, the user won't be active anymore 
            # the user is not going to be deleted from db because there may be pending messages to be sent from this user
            if user is not None and user.authenticate(password):
                # TODO check if it works
                user.is_active = False
                db.session.commit()
                logout_user()
                return redirect('/')
                
        # html template for unregistration confirmation
        return render_template('unregister.html', form=form, user = current_user)
        
    else:
        return redirect('/login')