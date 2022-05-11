# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, TextAreaField

class signup(FlaskForm):
    first_name = StringField('First name : ')
    last_name =  StringField('Last name : ')
    email = StringField("Email : ")
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

class EnteryForm(FlaskForm):
    service_name = StringField("Service Name: ")
    email = StringField("Email: ")
    password = StringField("Password: ")
    submit = SubmitField('Save')

class OCRForm(FlaskForm):
    input = TextAreaField("Results from OCR: ")
    submit = SubmitField('Submit Data')
