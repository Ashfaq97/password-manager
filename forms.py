# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, EmailField

class signup(FlaskForm):
    first_name = StringField('First name : ')
    last_name =  StringField('Last name : ')
    email = StringField("Email : ")
    submit = SubmitField('Sign up')
    
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

class FileDeleteForm(FlaskForm):
    filename = StringField("filename: ")
    submit = SubmitField("Delete")

class ServiceUpdateForm(FlaskForm):
    service_name = StringField("Service you are updating: ")
    new_email = EmailField("New Email:")
    new_pwd = PasswordField("New Password:")
    submit = SubmitField("Update Service")

class ServiceDeleteForm(FlaskForm):
    service_name = StringField("Service: ")
    submit = SubmitField("Delete Service")