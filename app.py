import logging
from datetime import datetime
from logging import config
from flask import Flask, render_template, redirect, url_for, request, make_response, send_from_directory
from wtforms import Form, BooleanField, StringField, validators

from database import db_session, init_db
from database.queries import unviewed_fictions, followed_fictions, watched_urls
from royalroad.models import ViewedFiction, WatchedURL
from royalroad.scraper import snapshot_url

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

init_db()

app = Flask(__name__)

# Pages for viewing fictions
number_of_entries_per_page = 50

@app.route("/")
def new():
    from_urls = watched_urls()
    if len(from_urls) == 0:
        default_url = ""
    else:
        default_url = from_urls[0].url
    page_url = request.args.get('url', default_url)
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

class WatchedURLForm(Form):
    url = StringField('url', validators=[validators.DataRequired()])
    alias = StringField('alias', validators=[validators.DataRequired()])
    active = BooleanField('active')

@app.route('/api/update_watched_url', methods=['POST'])
def update_watched_url():
    form = WatchedURLForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    action = request.form.get("action")
    app.logger.debug(f'update_watched_url action={action}')
    if action == 'delete':
        db_session.query(
            WatchedURL
        ).filter(
            WatchedURL.url == form.url.data
        ).delete(synchronize_session='fetch')
        db_session.commit()
    if action == 'save':
        db_session.query(
            WatchedURL
        ).filter(
            WatchedURL.url == form.url.data
        ).update({"alias": form.alias.data, "active": form.active.data }, synchronize_session="fetch")
        db_session.commit()
    if action == 'fetch':
        app.logger.info(f"Fetching fiction page requested, url={form.url.data}")
        snapshots = snapshot_url(form.url.data)
        for snapshot in snapshots:
            db_session.add(snapshot)
        db_session.commit()
    return redirect(url_for('data'))

@app.route('/api/create_watched_url', methods=['POST'])
def create_watched_url():
    form = WatchedURLForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    watched_url = WatchedURL(form.url.data, form.active.data, form.alias.data)
    app.logger.info(f'Creating watched url {watched_url}')
    db_session.add(watched_url)
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