# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from .columns import list_columns, update_column
from .datasets import list_datasets, create_dataset, get_dataset

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.route("/datasets", methods=["GET"])
def handle_list_datasets():
    """Handles GET requests to /v1/datasets."""
    return jsonify(list_datasets())


@app.route("/datasets", methods=["POST"])
def handle_post_datasets():
    """Handles POST requests to /v1/datasets."""
    return jsonify(create_dataset(request.files))


@app.route("/datasets/<name>", methods=["GET"])
def handle_get_dataset(name):
    """Handles GET requests to /v1/datasets/<name>."""
    return jsonify(get_dataset(name))


@app.route("/datasets/<dataset>/columns", methods=["GET"])
def handle_list_columns(dataset):
    """Handles GET requests to /v1/datasets/<dataset>/columns."""
    return jsonify(list_columns(dataset))


@app.route("/datasets/<dataset>/columns/<column>", methods=["PATCH"])
def handle_patch_column(dataset, column):
    """Handles PATCH requests to /v1/datasets/<dataset>/columns/<column>."""
    featuretype = request.get_json().get("featuretype")
    return jsonify(update_column(dataset, column, featuretype))


@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
@app.errorhandler(InternalServerError)
def handle_errors(e):
    """Handles exceptions raised by the API."""
    return jsonify({"message": e.description}), e.code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Datasets API"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--enable-cors", action="count")
    args = parser.parse_args()
    # Enable CORS
    if args.enable_cors:
        CORS(app)

    app.run(host="0.0.0.0", port=args.port)
