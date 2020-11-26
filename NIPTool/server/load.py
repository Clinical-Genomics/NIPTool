#!/usr/bin/env python

from flask import (
    jsonify,
    request,
    Blueprint,
    current_app)

from NIPTool.parse.batch import parse_batch_file
from NIPTool.load.batch import load_batch, load_samples, load_concentrations
from NIPTool.load.user import load_user
from NIPTool.models.validation import user_load_schema, batch_load_schema
from cerberus import Validator

import logging

LOG = logging.getLogger(__name__)

app = current_app
load_bp = Blueprint("load", __name__)


@load_bp.route("/batch", methods=["POST"])
def batch():
    """Function to load batch data into the database with rest"""

    request_data = request.form
    v = Validator(batch_load_schema)
    if not v.validate(request_data):
        message = "Incomplete batch load request"
        resp = jsonify({"message": message})
        resp.status_code = 400
        return resp

    batch_data = parse_batch_file(request_data['result_file'])
    load_batch(current_app.adapter, batch_data[0], request_data)
    load_samples(current_app.adapter, batch_data, request_data['project_name'])
    load_concentrations(current_app.adapter, request_data["concentrations"])

    message = "Data loaded into database"
    resp = jsonify({"message": message})
    resp.status_code = 200
    return resp


@load_bp.route("/user", methods=["POST"])
def user():
    """Function to load user into the database with rest"""

    request_data = request.form
    v = Validator(user_load_schema)
    if not v.validate(request_data):
        message = "Incomplete user load request"
        resp = jsonify({"message": message})
        resp.status_code = 400
        return resp

    load_user(current_app.adapter, request_data["email"], request_data["name"], request_data["role"])

    message = "Data loaded into database"
    resp = jsonify({"message": message})
    resp.status_code = 200
    return resp
