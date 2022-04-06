# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
class signup(FlaskForm):
    first_name = StringField('First name : ')
    last_name =  StringField('Last name : ')
    password  =  StringField('Passwrod : ')
    submit = SubmitField('Sign up')
class removeUser(FlaskForm):
    id = IntegerField("Id number of the user to remove : ")
    submit = SubmitField("Remove user")
