from flask import Flask, render_template, request, url_for

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'

import db
db.init_app(app)

@app.route("/", methods=['POST', 'GET'])
def hello():
    if request.method == "POST":
        userEmail = request.form['userEmail']
        return render_template('success.html')

    return render_template('index.html')



@app.route("/success", methods=["GET"])
def welcome():
    return render_template('success.html')



if __name__ == '__main__':
    app.run(debug=True)

