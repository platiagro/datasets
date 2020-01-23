"""WSGI server."""
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS

from .datasets import list_datasets

app = Flask(__name__)


@app.route("/", methods=["GET"])
def ping():
    """Handles GET requests to /."""
    return "pong"


@app.route("/v1/datasets", methods=["GET"])
def get_datasets():
    """Handles GET requests to /v1/datasets."""
    return jsonify(list_datasets())


if __name__ == "__main__":
    # Enable CORS
    if "--enable-cors" in sys.argv:
        CORS(app)

    app.run(host="0.0.0.0", port=8080)
