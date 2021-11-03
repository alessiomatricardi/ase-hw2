import datetime
import random

from flask import Flask

from monolith.auth import login_manager
from monolith.database import Message, User, Message_Recipient, db
from monolith.views import blueprints
from monolith import errors


def create_app(test_mode=False):
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # This allows us to test forms without WTForm token
    app.config['WTF_CSRF_ENABLED'] = False

    # Errors handling
    app.register_error_handler(401, errors.unauthorized)
    app.register_error_handler(403, errors.forbidden)
    app.register_error_handler(404, errors.page_not_found)

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        
        q = db.session.query(User).filter(User.email == 'user1@example.com')
        user = q.first()
        #print(user)
        if user is None:            
            if not test_mode: # TODO remove "not"
                populate_db()
                #print("No test mode")
            else:
                populate_db()
                #print("Test mode")
                """
                example = User()
                example.firstname = 'Admin'
                example.lastname = 'Admin'
                example.email = 'example@example.com'
                example.date_of_birth = datetime.datetime(2020, 10, 5)
                example.is_admin = True
                example.set_password('admin')
                db.session.add(example)
                db.session.commit()
                """
            

    return app

def populate_db():

    # add 3 users users
    i = 1
    example = User()
    example.email = 'user' + str(i) + '@example.com'
    example.firstname = 'user' + str(i)
    example.lastname = 'user' + str(i)
    example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
    example.is_admin = False
    example.set_password('user' + str(i))
    db.session.add(example)
    db.session.commit()

    i = 2
    example = User()
    example.email = 'user' + str(i) + '@example.com'
    example.firstname = 'user' + str(i)
    example.lastname = 'user' + str(i)
    example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
    example.is_admin = False
    example.set_password('user' + str(i))
    db.session.add(example)
    db.session.commit()

    i = 3
    example = User()
    example.email = 'user' + str(i) + '@example.com'
    example.firstname = 'user' + str(i)
    example.lastname = 'user' + str(i)
    example.date_of_birth = datetime.datetime(random.randint(1960, 2000), random.randint(1,12), random.randint(1,29))
    example.is_admin = False
    example.set_password('user' + str(i))
    db.session.add(example)
    db.session.commit()
    
    # create 10 random messages
    for i in range(1,11):
        message = Message()
        message.sender_id = i % 3 + 1
        message.content = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
        message.is_sent = random.randint(0,1)
        message.is_delivered = 0 if not message.is_sent else random.randint(0,1)
        message.deliver_time = datetime.datetime(2021, 10, 30, 23, 59) if message.is_delivered else datetime.datetime(2021, 11, random.randint(1,30), random.randint(0,23), random.randint(0,59)) 
        db.session.add(message)
    
    # create for each message at least 1 recipient
    for i in range(1,11):
        sender_id = db.session.query(Message).filter(Message.id == i).first().sender_id
        list_of_users_id = [sender_id]
        for j in range(1,random.randint(2,3)): # suppose that every message may have at least 4 recipients
            message_recipient = Message_Recipient()
            message_recipient.id = i
            recipient_id = random.randint(1,3)
            while recipient_id in list_of_users_id:
                recipient_id = random.randint(1,3)
            list_of_users_id.append(recipient_id)
            message_recipient.recipient_id = recipient_id
            message_recipient.read_time = datetime.datetime(2000, 1, 1)
            #
            # TODO find a way to set a datetime to null
            #
            db.session.add(message_recipient)

    db.session.commit()

    # TODO create default reports
    # TODO create default blacklists
  

app = create_app()

if __name__ == '__main__':
    app.run()
