"""WSGI server."""
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)


if __name__ == "__main__":
    # Enable CORS
    if "--enable-cors" in sys.argv:
        CORS(app)

    app.run(host="0.0.0.0", port=8080)
