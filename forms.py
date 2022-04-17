# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField

class signup(FlaskForm):
    first_name = StringField('First name : ')
    last_name =  StringField('Last name : ')
    email = StringField("Email : ")
    password  =  PasswordField('Passwrod : ')
    submit = SubmitField('Sign up')
class removeUser(FlaskForm):
    id = IntegerField("Id number of the user to remove : ")
    submit = SubmitField("Remove user")

class LoginForm(FlaskForm):
    first_name = StringField("First Name: ")
    last_name = StringField("Last Name: ")
    email = StringField("Email: ")
    submit = SubmitField('Continue')

class AuthCodeForm(FlaskForm):
    auth_field = PasswordField("Authentication Code: ")
    submit = SubmitField('Login')
