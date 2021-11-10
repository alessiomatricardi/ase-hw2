import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Email, Length
from wtforms import widgets, SelectMultipleField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileAllowed, FileRequired, FileField


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
    recipients = MultiCheckboxField('Recipients', choices=[]) # TODO write javascript script that set/remove the required attribute from the checkist
    content = f.TextAreaField('Content', validators=[DataRequired()])
    deliver_time = f.DateTimeField('Delivery time', validators=[DataRequired()], render_kw={'type': 'datetime-local'})
    attach_image = FileField()

class UnregisterForm(FlaskForm):
    password = f.PasswordField('Password', validators=[DataRequired()])
    display = ['password']


class ReportForm(FlaskForm):
    message_id = f.HiddenField(validators=[DataRequired()])


class HideForm(FlaskForm):
    message_id = f.HiddenField(validators=[DataRequired()])


class BlockForm(FlaskForm):
    user_id = f.HiddenField(validators=[DataRequired()])


class UnblockForm(FlaskForm):
    user_id = f.HiddenField(validators=[DataRequired()])


class ContentFilterForm(FlaskForm):
    filter_enabled = f.BooleanField()


class ProfilePictureForm(FlaskForm):
    image = FileField(validators=[FileRequired('File was empty!')])
    
class ModifyPersonalDataForm(FlaskForm):
    firstname = f.StringField('First name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    date_of_birth = f.DateField('Date of birth', render_kw = {'type' : 'date'})
    display = ['firstname', 'lastname', 'date_of_birth']

class ModifyPasswordForm(FlaskForm):
    old_password = f.PasswordField('Old password', validators=[DataRequired()])
    new_password = f.PasswordField('New password', validators=[
        DataRequired(),
        # this allow us to check the password on server-side
        Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
        )
    repeat_new_password = f.PasswordField('Repeat the new password', validators=[
        DataRequired(),
        # this allow us to check the password on server-side
        Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
        )
    
    display = ['old_password', 'new_password', 'repeat_new_password']
