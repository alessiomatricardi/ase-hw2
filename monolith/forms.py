import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    # TODO need to check if the email has the correct format e.g.
    # something @ domain . it/com/co.uk/etc etc...
    # investigate if there is a library to have the work done
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[
        DataRequired(), 
        Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ])
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']
