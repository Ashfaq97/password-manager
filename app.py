# app.py
import os
from os.path import join, dirname, realpath
from flask import Flask,render_template,url_for,redirect, request, send_from_directory, flash
from forms import signup, removeUser, LoginForm, AuthCodeForm, EnteryForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_mail import Mail, Message
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import json
import uuid
from datetime import datetime, timedelta
import time

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads')
UPLOAD_FOLDER = UPLOADS_PATH
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
login_manager = LoginManager()
mail = Mail()

app.config['SECRET_KEY'] = 'mysectretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

###############################
## SQL SECTION
###############################

#set up SQL db configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

 #set up db object and migration
db = SQLAlchemy(app)

Migrate(app,db)
login_manager.init_app(app)

#mail settings
#DO NOT TOUCH/MODIFY*****
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'comp680spring22@gmail.com'
app.config['MAIL_PASSWORD'] = 'comp680devteam'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail.init_app(app)


###############################
## MODELS
###############################

#The representation of a user in our database
class Users(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer,primary_key = True)
    num_attempts = db.Column(db.Integer, default=5)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    ocr_results = db.Column(db.Text)
    locked = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    locked_until = db.Column(db.DateTime)

    def __init__(self,first_name,last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.ocr_results = "{}"
    
    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"The user name is : {self.first_name} {self.last_name} OCR results: {self.ocr_results} "

#Helps with passwordless authentication
class AuthenticationStub(db.Model):
    __tablename__ = 'AuthStubs'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    auth_code = db.Column(db.Text)

    def __init__(self, email):
        self.email = email
        self.auth_code = str(uuid.uuid4())

    def get_email(self):
        return self.email
    
    def get_id(self):
        return str(self.id)
    
    def get_auth_code(self):
        return self.auth_code
    
    def __repr__(self):
        return f"(email: {self.email} code: {self.auth_code}) "

#ties uploaded files to user for ease of removal on user delete  
class UserFileInfo(db.Model):
    __tablename__ = 'UserFileInfo'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    filename = db.Column(db.Text)

    def __init__(self, email, filename):
        self.email = email
        self.filename = "".join([UPLOADS_PATH, filename])
    
    def get_email(self):
        return self.email
    
    def get_filename(self):
        return self.filename
    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"(email: {self.email}, filename: {self.filename}) "

class Infopage(db.Model):
    __tablename__ = "Infopage"
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)

    def __init__(self, service_name, email, password):
        self.service_name = service_name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"The service name is: {self.service_name} Email is : {self.email} and password is  : {self.password}"


###############################
## VIEW FUNTIONS/FORMS
###############################

@app.route('/')
def index():
    if current_user.is_anonymous:
        return redirect(url_for('login'))

    return render_template('home.html')

@app.route('/sign-up',methods=['GET','POST'])
def add_user():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    form = signup()

    if form.validate_on_submit():

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        user_obj = Users.query.filter_by(email=email).first()

        if user_obj == None:
            new_user = Users(first_name,last_name, email)
            user_auth_stub = AuthenticationStub(email)
            db.session.add(new_user)
            db.session.add(user_auth_stub)
            db.session.commit()
        else:
            return render_template('duplicate_user.html')


        return redirect(url_for('users_list'))
    return render_template('sign-up.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        if not current_user.locked:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('account_locked', user=current_user.email))
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', form=form)
    
    elif form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = Users.query.filter_by(first_name=first_name, last_name=last_name, email=email).first()

        if user:
            return redirect(url_for('send_auth_code', user=user.email))

@app.route('/login/<user>', methods=['GET', 'POST'])
def send_auth_code(user):
    auth_form = AuthCodeForm()
    user_obj = Users.query.filter_by(email=user).first()

    if user_obj.locked:
        return redirect(url_for('account_locked', user=user_obj.email))

    print('Attempts: ', user_obj.num_attempts)
    auth_stub = AuthenticationStub.query.filter_by(email=user).first()

    if user_obj.locked:
        return redirect(url_for('account_locked', user=user_obj.email))

    if request.method == 'GET':
        if user:
            msg = Message('Your Authentication Code', sender=app.config['MAIL_USERNAME'], recipients=[user])
            msg.body = "Your authentication code is: " + auth_stub.get_auth_code() + " \nUse this code to login."
            mail.send(msg)

            return render_template('auth_code.html', auth_form=auth_form)
        else:
            return redirect(url_for('login'))
    else:
        if auth_form.validate_on_submit():
            user_code = auth_form.auth_field.data

            if(user_code == auth_stub.get_auth_code()):
                login_user(user_obj)
                user_obj.num_attempts = 5
                db.session.commit()
                return redirect(url_for('index'))
            else:
                user_obj.num_attempts = user_obj.num_attempts - 1
                db.session.commit()
                if user_obj.num_attempts > 0:
                    return redirect(url_for('send_auth_code', user=user))
                else:
                    user_obj.locked = True
                    user_obj.locked_until = datetime.now() + timedelta(minutes=5)
                    db.session.commit()
                    return redirect(url_for('account_locked', user=user_obj.email))

@app.route('/locked/<user>', methods=['GET', 'POST'])
def account_locked(user):
    user_obj = Users.query.filter_by(email=user).first()
    current_time = datetime.now()

    print('Locked until: ', user_obj.locked_until)

    if not user_obj.locked:
        user_obj.num_attempts = 5
        user_obj.locked = False
        db.session.commit()
        return redirect(url_for('login'))
    elif current_time >= user_obj.locked_until:
        user_obj.num_attempts = 5
        user_obj.locked = False 
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('locked.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/list-users')
def users_list():
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    users = Users.query.all()
    return render_template('list-users.html',users=users)

@app.route('/delete', methods=['GET','POST'])
def remove_user():
    if current_user.is_anonymous:
        return redirect(url_for('index'))

    form = removeUser()

    if form.validate_on_submit():
        id = form.id.data
        user = Users.query.get(id)
        db.session.delete(user)
        db.session.commit()

        return redirect(url_for('users_list'))
    return render_template('remove-user.html',form=form)
   
   
   
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if current_user.is_anonymous:
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template('upload.html')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # If the user selects a genuine file then save it in the folder
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('process_file', name=filename))


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/ocr/<name>', methods=['GET'])
def process_file(name):
    if request.method == "GET":
        path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        ocr_dict = json.loads(current_user.ocr_results)
        ocr_dict[name] = pytesseract.image_to_string(path)
        current_user.ocr_results = json.dumps(ocr_dict)
        db.session.commit()
        return(redirect(url_for('users_list')))
       
       
 @app.route('/user_home')
def user_home():
    images = os.listdir('static/uploads')
    images = ['uploads/' + file for file in images]
    return render_template('user_home.html', images=images)
       

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()

@app.route("/EnteryForm", methods=["GET", "POST"])
def add_info():

    if current_user.is_anonymous:
        return redirect(url_for("login"))

    form = EnteryForm()

    
    if form.validate_on_submit():

        service_name = form.service_name.data
        email = form.email.data
        password = form.password.data
        new_service = Infopage(service_name, email, password)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for("info_list"))

    return render_template("EnteryForm.html", form=form)


@app.route("/info-list")
def info_list():
    if current_user.is_anonymous:
        return redirect(url_for("login"))

    infopage = Infopage.query.all()
    return render_template("info_list.html", infopage=infopage)


if __name__ == "__main__":
    app.run(debug=True, port=80)

