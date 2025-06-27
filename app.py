import logging
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, make_response
from wtforms import Form, BooleanField, StringField, validators

from database import db_session, init_db, queries
from royalroad.models import WatchedURL, NotInterestedInFiction
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
    from_urls = queries.watched_urls()
    if len(from_urls) == 0:
        default_url = ""
    else:
        default_url = from_urls[0].url
    page_url = request.args.get('url', default_url)
    fictions = queries.new_fictions(number_of_entries_per_page, from_url=page_url)
    return render_template('new_fictions.html', fictions=fictions, from_urls=from_urls)

@app.route("/dont_shows")
def dont_shows():
    return render_template('dont_shows.html', dont_shows=queries.dont_show_fictions())

@app.route("/watched_urls")
def watched_urls():
    return render_template('watched_urls.html', watched_urls=queries.watched_urls())

class WatchedURLForm(Form):
    url = StringField('url', validators=[validators.DataRequired()])
    alias = StringField('alias', validators=[validators.DataRequired()])
    active = BooleanField('active')

@app.route('/api/action_on_watched_url', methods=['POST'])
def action_on_watched_url():
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
            app.logger.debug(f"Snapshot {snapshot}")
            db_session.add(snapshot)
        db_session.commit()
    return redirect(url_for('watched_urls'))

@app.route('/api/create_watched_url', methods=['POST'])
def create_watched_url():
    form = WatchedURLForm(request.form)
    if not form.validate():
        return make_response({'message': form.errors}, 400)
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

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()