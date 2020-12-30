# -*- coding: utf-8 -*-
"""WSGI server."""
import argparse
import sys

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from datasets.columns import list_columns, update_column
from datasets.datasets import list_datasets, create_dataset, create_google_drive_dataset, \
    get_dataset, get_featuretypes, patch_dataset
from datasets.samples import init_datasets
from datasets.utils import to_snake_case

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """
    Handles GET requests to /.

    Returns
    -------
    str
    """
    return "pong"


@app.route("/datasets", methods=["GET"])
def handle_list_datasets():
    """
    Handles GET requests to /datasets.

    Returns
    -------
    str
    """
    return jsonify(list_datasets())


@app.route("/datasets", methods=["POST"])
def handle_post_datasets():
    """
    Handles POST requests to /datasets.

    Returns
    -------
    str
    """
    kwargs = None
    if request.data:
        kwargs = request.get_json(force=True)
        kwargs = {to_snake_case(k): v for k, v in kwargs.items()}

    if kwargs:
        return jsonify(create_google_drive_dataset(**kwargs))
    return jsonify(create_dataset(request.files))


@app.route("/datasets/<name>", methods=["GET"])
def handle_get_dataset(name):
    """
    Handles GET requests to /datasets/<name>.

    Parameters
    ----------
    name : str
        The dataset name.

    Returns
    -------
    str
    """
    page = request.args.get('page', 1)
    page_size = request.args.get('page_size', 10)

    return jsonify(get_dataset(name=name, page=page, page_size=page_size))


@app.route("/datasets/<name>", methods=["PATCH"])
def handle_patch_dataset(name):
    """
    Handles PATCH requests to /datasets/<name>.

    Parameters
    ----------
    name : str
        The dataset name.

    Returns
    -------
    str
    """
    return jsonify(patch_dataset(name, request.files))


@app.route("/datasets/<dataset>/columns", methods=["GET"])
def handle_list_columns(dataset):
    """
    Handles GET requests to /datasets/<dataset>/columns.

    Parameters
    ----------
    dataset : str
        The dataset to retrive columns.

    Returns
    -------
    str
    """
    return jsonify(list_columns(dataset))


@app.route("/datasets/<dataset>/columns/<column>", methods=["PATCH"])
def handle_patch_column(dataset, column):
    """
    Handles PATCH requests to /datasets/<dataset>/columns/<column>.

    Parameters
    ----------
    dataset : str
    column : str
        The column to be updated.

    Returns
    -------
    str
    """
    featuretype = request.get_json().get("featuretype")
    return jsonify(update_column(dataset, column, featuretype))


@app.route("/datasets/<dataset>/featuretypes", methods=["GET"])
def handle_get_featuretypes(dataset):
    """
    Handles GET requests to "/datasets/<dataset>/featuretypes.

    Parameters
    ----------
    dataset : str

    Returns
    -------
    str
    """
    featuretypes = get_featuretypes(dataset)
    response = make_response(featuretypes)
    response.headers.set('Content-Type', 'text/plain')
    response.headers.set('Content-Disposition', 'attachment', filename='featuretypes.txt')
    return response


@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
@app.errorhandler(InternalServerError)
def handle_errors(e):
    """
    Handles exceptions raised by the API.

    Returns
    -------
    str
    """
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
