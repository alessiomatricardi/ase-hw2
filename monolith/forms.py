import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Email, Length
from wtforms import widgets, SelectMultipleField
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired(), Email()])
    firstname = f.StringField('First name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[
        DataRequired(), 
        # this allow us to check the password on server-side
        Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
        )
    date_of_birth = f.DateField('Date of birth', render_kw = {'type' : 'date'})
    display = ['email', 'firstname', 'lastname', 'date_of_birth', 'password']


# class used to write a new message and decide the recipients
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MessageForm(FlaskForm):
    recipients = MultiCheckboxField('recipients', choices=[]) # TODO write javascript script that set/remove the required attribute from the checkist
    content = f.TextAreaField('content', validators=[DataRequired()])
    deliver_time = f.DateTimeField('deliver_time', validators=[DataRequired()], format="%d-%m-%Y, %H:%M")

    
class UnregisterForm(FlaskForm):
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['password']

class ReportForm(FlaskForm):
    message_id = f.TextField()

    def __init__(self, message_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_id.data = message_id