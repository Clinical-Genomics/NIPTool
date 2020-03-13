
import os
import logging

from flask import Flask, Blueprint
from pymongo import MongoClient

from newnipt.adapter.plugin import NiptAdapter
#from newnipt.server.views import blueprint

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
