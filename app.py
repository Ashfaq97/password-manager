from flask import Flask,request,render_template,return
import os
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'

import db
db.init_app(app)

@app.route("/")
def homepage():
    return render_template("homepage.html")

def Checklogin():
    EID = request.form['Email ID']

@app.route("/register")
def registerpage():
    UN = request.form['Username']
    UEID = request.form['User Email ID']

if __name__ == '__main__':
    app.run(debug=True)
