import logging

from flask import Flask
from pymongo import MongoClient
import yaml

from NIPTool.adapter.plugin import NiptAdapter
from NIPTool.server.login import login_bp, login_manager
from NIPTool.server.views import server_bp
from NIPTool.server.load import load_bp

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


def create_app(test=False):
    app = Flask(__name__)
    app.test = test
    if test:
        return app

    try:
        app.config.from_envvar('NIPT_CONFIG')
        configure_app(app)
    except:
        pass

    return app


def configure_app(app, config=None):
    if config:
        app.config = {**app.config, **yaml.safe_load(config)}
    app.config['SECRET_KEY'] = app.config['SECRET_KEY']
    client = MongoClient(app.config['DB_URI'])
    db_name = app.config['DB_NAME']
    app.client = client
    app.db = client[db_name]
    app.adapter = NiptAdapter(client, db_name=db_name)
    app.register_blueprint(login_bp)
    app.register_blueprint(server_bp)
    app.register_blueprint(load_bp)
    login_manager.init_app(app)

    if app.config['DEBUG'] == 1:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)

    return app
