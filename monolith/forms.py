import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


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
class MessageForm(FlaskForm):
    recipient = f.SelectMultipleField('recipient', validators=[DataRequired()]) # TODO change in a way that there could be more recipients
    content = f.TextAreaField('content', validators=[DataRequired()])
    display = ['recipient', 'content']