# app.py
import os
from os.path import join, dirname, realpath
from flask import Flask,render_template,url_for,redirect, request, send_from_directory, flash
from forms import signup, LoginForm, AuthCodeForm, EnteryForm, OCRForm, FileDeleteForm, ServiceUpdateForm, ServiceDeleteForm
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
import time #to satisfy possible dependencies

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
        self.filename = 'uploads/' + filename
    
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
    owner = db.Column(db.Text)
    service_name = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)

    def __init__(self, service_name, email, password):
        self.service_name = service_name
        self.owner = current_user.email
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

        if first_name == "":
            return redirect(url_for('add_user'))
        elif last_name == "":
            return redirect(url_for('add_user'))
        elif email == "":
            return redirect(url_for('add_user'))

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
        else:
            new_form = LoginForm()
            flash("Invalid user information.")
            return render_template('login.html', form=new_form)

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

    auth_stub = AuthenticationStub.query.filter_by(email=current_user.email).first()
    fptrs = UserFileInfo.query.filter_by(email=current_user.email)
    pwds = Infopage.query.filter_by(owner=current_user.email)

    if fptrs:
        for ptr in fptrs:
            db.session.delete(ptr)
    
    if pwds:
        for pwd in pwds:
            db.session.delete(pwd)

    if auth_stub:
        db.session.delete(auth_stub)

    usr = Users.query.get(current_user.id)
    db.session.delete(usr)
    db.session.commit()
    flash("Your account was successfully deleted.")

    return redirect(url_for('login'))

@app.route('/delete_ocr', methods=['GET', 'POST'])
def delete_user_file_info():
    file_form = FileDeleteForm()

    if current_user.is_anonymous:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('delete_files.html', frm=file_form)
    else:
        if file_form.validate_on_submit():
            fn = file_form.filename.data
            usr = Users.query.get(current_user.id)
            fp = None
            fptrs = UserFileInfo.query.filter_by(email=usr.email)
            for ptr in fptrs:
                if ptr.filename == 'uploads/' + fn:
                    fp = ptr
                    break
            
            if fp:
                UserFileInfo.query.filter(UserFileInfo.id == fp.id).delete()
                ocr_dict = json.loads(usr.ocr_results)
                ocr_dict.pop(fn)
                usr.ocr_results = json.dumps(ocr_dict)
                db.session.commit()
                flash('Success')
            
    return redirect(url_for('delete_user_file_info', frm=file_form))

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
            usr_file_ref = UserFileInfo.query.filter(UserFileInfo.email==current_user.email, UserFileInfo.filename=='uploads/' + filename).first()

            if usr_file_ref != None:
                print("Duplicate File")
            else:
                user_file_info = UserFileInfo(current_user.email, filename)
                db.session.add(user_file_info)
                db.session.commit()

            return redirect(url_for('process_file', name=filename))


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/ocr/<name>', methods=['GET', 'POST'])
def process_file(name):
    ocrf = OCRForm()

    if request.method == "GET":
        path = os.path.join(app.config['UPLOAD_FOLDER'], name)
        ocrf.input.data = pytesseract.image_to_string(path)
        #replace with render to seperate page
        return render_template('ocr_results.html', name=name, ocrf=ocrf)
    else:
        if ocrf.validate_on_submit():
            ocr_dict = json.loads(current_user.ocr_results)
            ocr_dict[name] = ocrf.input.data
            current_user.ocr_results = json.dumps(ocr_dict)
            db.session.commit()
            return redirect(url_for('users_list'))
       
       
@app.route('/user_home')
def user_home():
    images = []
    fptrs = UserFileInfo.query.filter_by(email=current_user.email)
    
    if fptrs:
        for ptr in fptrs:
            images.append(ptr.filename)

    return render_template('user_home.html', images=images)
       

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()

@app.route("/add_service", methods=["GET", "POST"])
def add_info():

    if current_user.is_anonymous:
        return redirect(url_for("login"))

    form = EnteryForm()

    if request.method == 'GET':
        return render_template('EnteryForm.html', form=form)
    else:
        if form.validate_on_submit():
            name = form.service_name.data
            email = form.email.data
            password = form.password.data

            if name == "":
                flash('Service name cannot be empty')
                return render_template('EnteryForm.html', form=form)
            elif email == "":
                flash('Email cannot be empty')
                return render_template('EnteryForm.html', form=form)
            elif password == "":
                flash('Password cannot be empty')
                return render_template('EnteryForm.html', form=form)
            else:
                service = Infopage.query.filter(Infopage.owner==current_user.email, Infopage.service_name==name).first()

                if service:
                    flash('This service already exists try updating it using either the link in the navigation bar or from your profile')
                    return render_template('EnteryForm.html', form=form)
                else:
                    new_service = Infopage(name, email, password)
                    db.session.add(new_service)
                    db.session.commit()
    
    return redirect(url_for('info_list'))

@app.route("/service/update", methods=["GET", "POST"])
def update_info():
    if current_user.is_anonymous:
        return redirect(url_for('login'))

    service_form = ServiceUpdateForm()

    if request.method == 'GET':
        render_template('update_service.html', svcf=service_form)
    else:
        if service_form.validate_on_submit():
            name = service_form.service_name.data
            svc_email = service_form.new_email.data
            svc_pwd = service_form.new_pwd.data

            if name == "":
                flash("You must enter the name of the service you are updating")
                return render_template('update_service.html', svcf=service_form, error=True)
            else:
                service =  Infopage.query.filter(Infopage.owner==current_user.email, Infopage.service_name==name).first()
                
                if service:
                    if svc_email:
                        service.email = svc_email
                    if svc_pwd:
                        service.password = svc_pwd

                    db.session.commit()
                    flash(f'The service {name} has been updated')
                else:
                    flash('No such service')
                    return render_template('update_service.html', svcf=service_form, error=True)
                    
    return render_template('update_service.html', svcf=service_form, error=False)

@app.route("/service/delete", methods=["GET", "POST"])
def delete_info():
    delete_service_form = ServiceDeleteForm()

    if request.method == 'GET':
        return render_template('delete_service.html', dsvcf=delete_service_form)
    else:
        if delete_service_form.validate_on_submit():
            name = delete_service_form.service_name.data

            if name == "":
                flash('You must enter a service name')
                return render_template('delete_service.html', dsvcf=delete_service_form, error=True)
            else:
                service = Infopage.query.filter(Infopage.owner==current_user.email, Infopage.service_name==name).first()

                if service:
                    db.session.delete(service)
                    db.session.commit()
                    flash('The service has been deleted')
                else:
                    flash('No such service')
                    return render_template('delete_service.html', dsvcf=delete_service_form, error=True)
    
    return render_template('delete_service.html', dsvcf=delete_service_form, error=False)

@app.route("/info-list")
def info_list():
    if current_user.is_anonymous:
        return redirect(url_for("login"))

    infopage = Infopage.query.filter_by(owner=current_user.email)
    return render_template("info_list.html", infopage=infopage)


if __name__ == "__main__":
    app.run(debug=True, port=80)

