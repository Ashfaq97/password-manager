# app.py
import os
from os.path import join, dirname, realpath
from flask import Flask,render_template,url_for,redirect, request, send_from_directory
from forms import signup, removeUser
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads')
UPLOAD_FOLDER = UPLOADS_PATH
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

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


###############################
## MODELS
###############################

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer,primary_key = True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    password = db.Column(db.Text)

    def __init__(self,first_name,last_name,password):
        self.first_name = first_name
        self.last_name = last_name
        self.password= password
    def __repr__(self):
        return f"The user name is : {self.first_name} {self.last_name} and password is {self.password} "
###############################
## VIEW FUNTIONS/FORMS
###############################

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/sign-up',methods=['GET','POST'])
def add_user():
    form = signup()

    if form.validate_on_submit():

        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data

        new_user = Users(first_name,last_name,password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users_list'))
    return render_template('sign-up.html',form=form)
@app.route('/list-users')
def users_list():

    users = Users.query.all()
    return render_template('list-users.html',users=users)

@app.route('/delete', methods=['GET','POST'])
def remove_user():

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
            return redirect(url_for('download_file', name=filename))


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run(debug=True)
