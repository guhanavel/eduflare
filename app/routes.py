import flask
from flask import current_app as app


@app.route('/a')
def home():
    return flask.redirect('/')