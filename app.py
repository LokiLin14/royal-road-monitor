from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, make_response, send_from_directory
from wtforms import Form, BooleanField, StringField, validators

from database import db_session, init_db
from database.queries import unviewed_fictions, followed_fictions, watched_urls
from royalroad.models import ViewedFiction
from royalroad.scraper import snapshot_url

init_db()
app = Flask(__name__)

# Pages for viewing fictions
number_of_entries_per_page = 20

@app.route("/")
def new():
    from_urls = watched_urls()
    if len(from_urls) == 0:
        default_url = ""
    else:
        default_url = from_urls[0].url
    page_url = request.args.get('url', default_url)
    print(page_url)
    fictions = unviewed_fictions(number_of_entries_per_page, from_url=page_url)
    return render_template('homepage.html', fictions=fictions, from_urls=from_urls)

@app.route("/watched")
def watched():
    fictions = followed_fictions(number_of_entries_per_page)
    return render_template('watched.html', fictions=fictions)
@app.route("/data")
def data():
    return render_template('data.html', watched_urls=watched_urls())

@app.route("/fetch_data", methods=['POST'])
def fetch_data():
    print("Fetching data requested")
    snapshots = snapshot_url('https://www.royalroad.com/fictions/rising-stars')
    for snapshot in snapshots:
        db_session.add(snapshot)
    db_session.commit()
    return redirect(url_for('data'))

class ViewFictionForm(Form):
    url = StringField('URL', validators=[validators.DataRequired(), validators.Length(max=200)])
    interested = BooleanField('INTERESTED')

@app.route("/view", methods=['POST'])
def view():
    form = ViewFictionForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    print(form.interested.data)
    db_session.add(ViewedFiction(url=form.url.data, marked_time=datetime.now(), interested=form.interested.data))
    db_session.commit()
    return make_response({'message': f'Marked fiction as viewed, interested={form.interested.data}'}, 200)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()