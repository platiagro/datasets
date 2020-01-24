"""WSGI server."""
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from .datasets import list_datasets, create_dataset

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.route("/v1/datasets", methods=["GET"])
def get_datasets():
    """Handles GET requests to /v1/datasets."""
    return jsonify(list_datasets())


@app.route("/v1/datasets", methods=["POST"])
def post_datasets():
    """Handles POST requests to /v1/datasets."""
    return jsonify(create_dataset(request.files))


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({"message": e.description}), 400


if __name__ == "__main__":
    # Enable CORS
    if "--enable-cors" in sys.argv:
        CORS(app)

    app.run(host="0.0.0.0", port=8080)
