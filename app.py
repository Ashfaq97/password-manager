from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'

import db
db.init_app(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    app.run(debug=True)