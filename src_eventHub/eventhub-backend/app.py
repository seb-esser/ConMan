from flask import Flask, request, jsonify, render_template, json
from flask_cors import CORS, cross_origin
from flask_socketio import send, emit, SocketIO

from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resource={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@socketio.event
def connect():
    print("[WS]: New client has connected via websocket. ")


@socketio.event
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")


if __name__ == '__main__':
    print("Starting server ... ")
    socketio.run(app)
