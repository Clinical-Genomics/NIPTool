from flask import url_for, redirect, render_template, request, Blueprint, current_app

from werkzeug.contrib.fixers import ProxyFix

from flask_login import LoginManager
from flask_mail import Mail
from flask_oauthlib.client import OAuth

import os
import logging

from flask import Flask
from pymongo import MongoClient

from newnipt.adapter.plugin import NiptAdapter

blueprint = Blueprint('server', __name__ )

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def create_app(test = False):
    app = Flask(__name__, instance_relative_config=True)
    if not test:
        app.config.from_object(f"{__name__}.config")
        client = MongoClient(app.config['DB_URI'])
        db_name = app.config['DB_NAME']
        app.client = client
        app.db = client[db_name]
        app.adapter = NiptAdapter(client, db_name = db_name)
        app.analysis_path = app.config['ANALYSIS_PATH']
        app.register_blueprint(blueprint)

        if app.config['DEBUG']==1:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)

    return app

app = create_app()

app.wsgi_app = ProxyFix(app.wsgi_app)



mail = Mail(app)
login_manager = LoginManager(app)
oauth = OAuth(app)
google = oauth.remote_app('google', app_key='GOOGLE')
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.refresh_view = 'reauth'