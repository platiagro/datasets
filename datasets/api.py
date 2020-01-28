"""WSGI server."""
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from .columns import list_columns
from .datasets import list_datasets, create_dataset, get_dataset

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.route("/v1/datasets", methods=["GET"])
def handle_list_datasets():
    """Handles GET requests to /v1/datasets."""
    return jsonify(list_datasets())


@app.route("/v1/datasets", methods=["POST"])
def handle_post_datasets():
    """Handles POST requests to /v1/datasets."""
    return jsonify(create_dataset(request.files))


@app.route("/v1/datasets/<name>", methods=["GET"])
def handle_get_dataset(name):
    """Handles GET requests to /v1/datasets/<name>."""
    return jsonify(get_dataset(name))


@app.route("/v1/datasets/<dataset>/columns", methods=["GET"])
def handle_list_columns(dataset):
    """Handles GET requests to /v1/datasets/<dataset>/columns."""
    return jsonify(list_columns(dataset))


@app.errorhandler(BadRequest)
@app.errorhandler(NotFound)
def handle_bad_request(e):
    return jsonify({"message": e.description}), e.code


@app.errorhandler(InternalServerError)
def handle_internal_server_error(e):
    return jsonify({"message": e.description}), 500


if __name__ == "__main__":
    # Enable CORS
    if "--enable-cors" in sys.argv:
        CORS(app)

    app.run(host="0.0.0.0", port=8080)
