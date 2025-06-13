from datetime import datetime

from flask import Flask, render_template
from database import db_session, init_db
from database.queries import interested_fictions, add_data

init_db()
app = Flask(__name__)

@app.route("/")
def new():
    fictions_displayed = 10
    fictions = interested_fictions(fictions_displayed)
    return render_template('homepage.html', fictions=fictions)

@app.route("/data")
def data():
    return render_template('data.html')

@app.route("/watched")
def watched():
    fictions = [
        {
            'title' : 'Big Power Fantasy 1',
            'description' : 'The hero becomes increasingly powerful!'
        }
    ]
    return render_template('watched.html', fictions=fictions)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
