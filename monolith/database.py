from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    has_picture = db.Column(db.Boolean, default=False)  # has the user a personal profile picture

    '''
    2nd priority stuffs
    lottery_points = db.Column(db.integer, default=0)
    content_filter_enabled = db.Column(db.Boolean, default=False)
    '''

    # Relatioships with other classes
    # sent_messages = db.relationship('Messages', backref='sender', lazy=True)
    # received_messages = db.relationship('Message_Recipients', backref='recipient', lazy=True)
    # reported_messages = db.relationship('Reports', backref='reporter', lazy=True)
    # blocked_users = db.relationship('Blacklist', backref='blocked', lazy=True)
    # blocking_users = db.relationship('Blacklist', backref='blocking', lazy=True)

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Messages(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Unicode(700), nullable=False)
    is_sent = db.Column(db.Boolean, default=False)
    deliver_time = db.Column(db.DateTime)

    # Relatioship with other classes
    # recipients = db.relationship('Message_Recipients', backref='message', lazy=True)
    # reports = db.relationship('Reports', backref='message_report', lazy=True)

    def __init__(self, *args, **kw):
        super(Messages, self).__init__(*args, **kw)

    def set_sender(self, id):
        self.sender_id = id

    def set_content(self, content):
        self.content = content

    def get_id(self):
        return self.id


class Message_Recipients(db.Model):

    __tablename__ = 'message_recipients'

    id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_time = db.Column(db.DateTime)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            id, recipient_id,
        ),
    )

    def __init__(self, *args, **kw):
        super(Message_Recipients, self).__init__(*args, **kw)

    def get_id(self):
        return self.id

    def get_recipient_id(self):
        return self.recipient_id


class Reports(db.Model):

    __tablename__ = 'reports'

    reporting_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    report_time = db.Column(db.DateTime)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            reporting_user_id, message_id,
        ),
    )

    '''
    def __init__(self, *args, **kw):
        super(Reports, self).__init__(*args, **kw)
   
    def get_reporting_user_id(self):
        return selg.reporting_user_id
    '''


class Blacklist (db.Model):

    __tablename__ = 'blacklist'

    blocking_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocked_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            blocking_user_id, blocked_user_id,
        ),
    )


"""
__table_args__ = (
    db.PrimaryKeyConstraint(
        transaction_id, customer_id,
        ),
    )


__table_args__ = (
        db.ForeignKeyConstraint(
            ['pptr_perf_id', 'pptr_plan_id', 'pptr_tran_id'],
            ['perfil.perf_id', 'plano.plan_id', 'transacao.tran_id'],
            ['fk_Perfil_Plano_Transacao_Perfil1', 'fk_Perfil_Plano_Transacao_Plano1', 'fk_Perfil_Plano_Transacao_Transacao1']
        ),
    )
"""
