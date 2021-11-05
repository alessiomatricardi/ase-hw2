import datetime
import os
import random

from flask import Flask

from monolith.auth import login_manager
from monolith.database import Message, User, Message_Recipient, db
from monolith.views import blueprints
from monolith import errors

def create_app():
    #app = Flask(__name__, static_folder='/home/davide/Scrivania/ase-hw2/static/')
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['UPLOAD_FOLDER'] = app.static_folder # !! SET THE PROPER PATH TO THE UPLOAD FOLDER !! 


    # This allows us to test forms without WTForm token
    app.config['WTF_CSRF_ENABLED'] = False

    # Errors handling
    app.register_error_handler(401, errors.unauthorized)
    app.register_error_handler(403, errors.forbidden)
    app.register_error_handler(404, errors.page_not_found)
    app.register_error_handler(409, errors.conflict)
    app.register_error_handler(500, errors.internal_server)

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        #print(user)
        if user is None:            
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.date_of_birth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
