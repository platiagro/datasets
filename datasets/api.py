# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from .columns import list_columns, update_column
from .datasets import list_datasets, create_dataset, get_dataset, get_featuretypes, \
    patch_dataset
from .samples import init_datasets

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.route("/datasets", methods=["GET"])
def handle_list_datasets():
    """Handles GET requests to /datasets."""
    return jsonify(list_datasets())


@app.route("/datasets", methods=["POST"])
def handle_post_datasets():
    """Handles POST requests to /datasets."""
    return jsonify(create_dataset(request.files))


@app.route("/datasets/<name>", methods=["GET"])
def handle_get_dataset(name):
    """Handles GET requests to /datasets/<name>."""
    page = request.args.get('page')
    page_size = request.args.get('page_size')
    return jsonify(get_dataset(name, page, page_size))


@app.route("/datasets/<name>", methods=["PATCH"])
def handle_patch_dataset(name):
    """Handles PATCH requests to /datasets/<name>."""
    return jsonify(patch_dataset(name, request.files))


@app.route("/datasets/<dataset>/columns", methods=["GET"])
def handle_list_columns(dataset):
    """Handles GET requests to /datasets/<dataset>/columns."""
    return jsonify(list_columns(dataset))


@app.route("/datasets/<dataset>/columns/<column>", methods=["PATCH"])
def handle_patch_column(dataset, column):
    """Handles PATCH requests to /datasets/<dataset>/columns/<column>."""
    featuretype = request.get_json().get("featuretype")
    return jsonify(update_column(dataset, column, featuretype))


@app.route("/datasets/<dataset>/featuretypes", methods=["GET"])
def handle_get_featuretypes(dataset):
    """Handles GET requests to "/datasets/<dataset>/featuretypes."""
    featuretypes = get_featuretypes(dataset)
    response = make_response(featuretypes)
    response.headers.set('Content-Type', 'text/plain')
    response.headers.set('Content-Disposition', 'attachment', filename='featuretypes.txt')
    return response


@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
@app.errorhandler(InternalServerError)
def handle_errors(e):
    """Handles exceptions raised by the API."""
    return jsonify({"message": e.description}), e.code


def parse_args(args):
    """Takes argv and parses API options."""
    parser = argparse.ArgumentParser(
        description="Datasets API"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--enable-cors", action="count")
    parser.add_argument(
        "--debug", action="count", help="Enable debug"
    )
    parser.add_argument(
        "--samples-config", help="Path to sample datasets config file."
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # Enable CORS if required
    if args.enable_cors:
        CORS(app)

    # Install sample datasets if required
    if args.samples_config:
        init_datasets(args.samples_config)

    app.run(host="0.0.0.0", port=args.port, debug=args.debug)
