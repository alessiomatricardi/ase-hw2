import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import widgets, SelectMultipleField


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']

# class used to write a new message and decide the recipients
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MessageForm(FlaskForm):
    string_of_recipients = ['1\r\n2\r\n3\r\n']
    list_of_recipients = string_of_recipients[0].split()
    # create a list of value/description tuples
    recipients_pair = [(x, x) for x in list_of_recipients]
    recipients = MultiCheckboxField('Label', choices=recipients_pair) # TODO write javascript script that set/remove the required attribute from the checkist
    content = f.TextAreaField('content', validators=[DataRequired()])
    #display = ['recipient', 'content']

class BottleForm(FlaskForm):
    deliver_time = f.DateTimeField('deliver_time', validators=[DataRequired()])