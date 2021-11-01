from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# default library salt length is 8
# adjusting it to 16 allow us to improve the strongness of the password
_SALT_LENGTH = 16

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), unique=True, nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    has_picture = db.Column(db.Boolean, default=False)  # has the user a personal profile picture
    lottery_points = db.Column(db.Integer, default=0)

    '''
    TODO 2nd priority stuffs
    
    content_filter_enabled = db.Column(db.Boolean, default=False)
    '''

    # Relatioships with other classes
    sent_messages = db.relationship('Message', backref='sender', lazy=True)
    received_messages = db.relationship('Message_Recipient', backref='recipient', lazy=True)
    reported_messages = db.relationship('Report', backref='reporter', lazy=True)
    # blocked_users = db.relationship('Blacklist', backref='blocked', foreign_keys='blocked_user_id', lazy=True)
    # blocking_users = db.relationship('Blacklist', backref='blocking', foreign_keys='blocking_user_id', lazy=True)

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        '''
        According to https://werkzeug.palletsprojects.com/en/2.0.x/utils/#werkzeug.security.generate_password_hash
        generate_password_hash returns a string in the format below
        pbkdf2:sha256:num_of_iterations$salt$hash
        '''
        self.password = generate_password_hash(password, salt_length = _SALT_LENGTH)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        # an user no more active couldn't authenticate himself
        if not self.is_active:
            return False
        
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Message(db.Model):

    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Unicode(700), nullable=False)
    is_sent = db.Column(db.Boolean, default = False) 
    is_delivered = db.Column(db.Boolean, default = False)
    deliver_time = db.Column(db.DateTime)

    # Relatioship with other classes
    recipients = db.relationship('Message_Recipient', backref='message_recipient.recipient_id', lazy=True)
    reports = db.relationship('Report', backref='message_report', lazy=True)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def set_sender(self, id):
        self.sender_id = id

    def set_content(self, content):
        self.content = content

    #
    # TODO add setter methods to set the deliver_time and the is_sent variables
    #

    def get_id(self):
        return self.id


class Message_Recipient(db.Model):

    __tablename__ = 'message_recipient'

    id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_time = db.Column(db.DateTime)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            id, recipient_id,
        ),
    )

    def __init__(self, *args, **kw):
        super(Message_Recipient, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def get_recipient_id(self):
        return self.recipient_id


class Report(db.Model):

    __tablename__ = 'report'

    reporting_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    report_time = db.Column(db.DateTime)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            reporting_user_id, message_id,
        ),
    )


    def __init__(self, *args, **kw):
        super(Report, self).__init__(*args, **kw)


class Blacklist (db.Model):

    __tablename__ = 'blacklist'

    blocking_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            blocking_user_id, blocked_user_id,
        ),
    )

    def __init__(self, *args, **kw):
        super(Blacklist, self).__init__(*args, **kw)
