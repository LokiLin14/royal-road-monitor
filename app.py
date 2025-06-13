from flask import Flask, render_template, redirect, url_for

from database import db_session, init_db
from database.queries import interested_fictions
from royalroad.scraper import snapshot_url

init_db()
app = Flask(__name__)

@app.route("/")
def new():
    fictions_displayed = 40
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

@app.route("/fetch_data", methods=['POST'])
def fetch_data():
    print("Fetching data requested")
    snapshots = snapshot_url('https://www.royalroad.com/fictions/rising-stars')
    for snapshot in snapshots:
        db_session.add(snapshot)
    db_session.commit()
    return redirect(url_for('data'))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
