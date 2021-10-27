import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Email, Length
from wtforms import widgets, SelectMultipleField
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired(), Email()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[
        DataRequired(), 
        # this allow us to check the password on server-side
        Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
        )
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']


# class used to write a new message and decide the recipients
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MessageForm(FlaskForm):
    recipients = MultiCheckboxField('Label', choices=[]) # TODO write javascript script that set/remove the required attribute from the checkist
    content = f.TextAreaField('content', validators=[DataRequired()])
    deliver_time = f.DateTimeField('deliver_time', validators=[DataRequired()], format="%d-%m-%Y, %H:%M")

    
class UnregisterForm(FlaskForm):
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['password']