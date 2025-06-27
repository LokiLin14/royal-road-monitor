"""
This app is a webserver that tracks if any new fictions have appeared on a RoyalRoad page.
It can be configured to track Rising Stars, Ongoing Fictions, Top Rated, etc.
"""
__version__ = "0.0.1"

import logging
import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, BooleanField, StringField, validators

from .database import init_db, queries
from .royalroad.models import WatchedURL, NotInterestedInFiction
from .royalroad.scraper import snapshot_url

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)

# app.config["CRON_KEY"] = SECRET_STRING          # Configures the string needed to call '/api/cron',
                                                  # recommended to set it via the "FLASK_CRON_KEY" env variable
app.config["NUM_ENTRIES_ON_NEW_PAGE"] = 50        # Configures the number of entries displayed in '/'
app.config["NUM_ENTRIES_ON_DONT_SHOW_PAGE"] = 50  # Configures the number of entries displayed in '/dont_shows'
app.config["DB_DIR"] = "./"
app.config.from_prefixed_env(prefix="FLASK")

# Initialise the database
db_dir = os.path.abspath(app.config["DB_DIR"])
engine = create_engine(f'sqlite:///{db_dir}/test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=engine))
init_db(engine)

@app.route("/")
def new():
    from_urls = queries.watched_urls(db_session)
    if len(from_urls) == 0:
        default_url = ""
    else:
        default_url = from_urls[0].url
    page_url = request.args.get('url', default_url)
    fictions = queries.new_fictions(db_session, app.config["NUM_ENTRIES_ON_NEW_PAGE"], from_url=page_url)
    return render_template('new_fictions.html', fictions=fictions, from_urls=from_urls)

@app.route("/dont_shows")
def dont_shows():
    dont_shows_entries = queries.dont_show_fictions(db_session, app.config["NUM_ENTRIES_ON_DONT_SHOW_PAGE"])
    return render_template('dont_shows.html', dont_shows=dont_shows_entries)

@app.route("/watched_urls")
def watched_urls():
    return render_template('watched_urls.html', watched_urls=queries.watched_urls(db_session))

class WatchedURLForm(Form):
    url = StringField('url', validators=[validators.DataRequired()])
    alias = StringField('alias', validators=[validators.DataRequired()])
    active = BooleanField('active')

def index_fiction_page(url: str):
    app.logger.info(f"Indexing fiction page, url={url}")
    snapshots = snapshot_url(url)
    for snapshot in snapshots:
        app.logger.debug(f"Snapshot {snapshot}")
        db_session.add(snapshot)
    db_session.commit()

@app.route('/api/action_on_watched_url', methods=['POST'])
def action_on_watched_url():
    form = WatchedURLForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    action = request.form.get("action")
    app.logger.debug(f'update_watched_url action={action}')
    if action == 'delete':
        app.logger.info(f"Deleting watched url, url={form.url.data}")
        db_session.query(
            WatchedURL
        ).filter(
            WatchedURL.url == form.url.data
        ).delete(synchronize_session='fetch')
        db_session.commit()
    if action == 'save':
        app.logger.info(f"Saving changes of watched url, url={form.url.data}, alias={form.alias.data}, active={form.active.data}")
        db_session.query(
            WatchedURL
        ).filter(
            WatchedURL.url == form.url.data
        ).update({"alias": form.alias.data, "active": form.active.data }, synchronize_session="fetch")
        db_session.commit()
    if action == 'fetch':
        app.logger.info(f"Fetching watched url requested, url={form.url.data}")
        index_fiction_page(form.url.data)
    return redirect(url_for('watched_urls'))

@app.route('/api/create_watched_url', methods=['POST'])
def create_watched_url():
    form = WatchedURLForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    app.logger.info(f"Creating watched url, url={form.url.data}, alias={form.alias.data}, active={form.active.data}")
    watched_url = WatchedURL(form.url.data, form.active.data, form.alias.data)
    app.logger.info(f'Creating watched url {watched_url}')
    db_session.add(watched_url)
    db_session.commit()
    return redirect(url_for('watched_urls'))

class DontShowFictionForm(Form):
    url = StringField('URL', validators=[validators.DataRequired(), validators.Length(max=200)])

@app.route('/api/dont_show_again', methods=['POST'])
def dont_show_again():
    form = DontShowFictionForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    app.logger.info(f'Marking fiction as dont show again, url={form.url.data}')
    db_session.add(NotInterestedInFiction(url=form.url.data, marked_time=datetime.now()))
    db_session.commit()
    return make_response({'message': f'Marked fiction as dont show'}, 200)

@app.route('/api/delete_dont_show', methods=['POST'])
def delete_dont_show():
    form = DontShowFictionForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
    app.logger.info(f'Removing dont show mark from fiction, url={form.url.data}')
    db_session.query(NotInterestedInFiction).filter(NotInterestedInFiction.url == form.url.data).delete()
    db_session.commit()
    return make_response({'message': f'Removed dont show'}, 200)

@app.route('/api/cron')
def cron():
    cron_key = request.args.get('cron_key')
    if cron_key is None or cron_key != app.config['CRON_KEY']:
        app.logger.error(f'Invalid cron_key {cron_key}')
        return make_response({'message': 'Invalid cron_key'}, 400)
    app.logger.info("Valid cron_key presented, fetching all watched urls")
    for watched_url in queries.watched_urls(db_session):
        if not watched_url.active:
            app.logger.info(f"Watched URL not active, watched_url={watched_url}")
        else:
            app.logger.info(f"Watched URL active, watched_url={watched_url}")
            index_fiction_page(watched_url.url)
    return make_response({'message': 'All watched urls have been fetched'}, 200)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()