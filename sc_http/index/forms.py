from flask_wtf import Form, FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Email

class LoginForm(FlaskForm):
    login = StringField('', [DataRequired()])
    password = PasswordField('', [DataRequired()])

class RegisterForm(FlaskForm):
    name = StringField('', [DataRequired()])
    login = StringField('', [DataRequired()])
    password = PasswordField('', [DataRequired()])
    confirm = PasswordField('', [DataRequired(), EqualTo('password', message='Password much match')])
    email = StringField('', [DataRequired(), Email()])
