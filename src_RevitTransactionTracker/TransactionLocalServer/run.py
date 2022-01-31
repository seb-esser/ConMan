from flask import Flask, request, jsonify, render_template, json
from werkzeug.exceptions import HTTPException
from flask_socketio import send, emit, SocketIO
from flask_cors import CORS, cross_origin
from static.globalVariables import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resource={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")


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
def render_landing_page():
    return render_template("index.html")


@app.route('/api/ReportTransaction', methods=["POST"])
def report_transaction():
    """
    handles an incoming REST request under /api/ReportTransaction
    :return:
    """
    try:

        # decode request args
        bdy = request.json
        print('[REST]: ' + str(bdy))
        messages.append(bdy)

        # respond REST request with a json object
        response_json = {
            "status": "ok"
        }

        # emit websocket message
        socketio.emit('newTransaction', bdy)

        return jsonify(response_json)

    except HTTPException as e:
        handle_exception(e)


@socketio.on('message')
@cross_origin()
def handle_message(data):
    print('[WS] received message: ' + data)


@socketio.event
def connect():
    print("[WS]: New client has connected via websocket. ")


@socketio.event
def disconnect():
    print("[WS]: Existing client has disconnected via websocket. ")


if __name__ == "__main__":
    print("Starting server ... ")
    socketio.run(app)

    # In order to run this server properly, the following packages are required:
    # - Flask_SocketIO (pip install flask_socketio)
    # - eventlet (pip install eventlet)
    # Debug or run config: `python run.py` (standard python config in pycharm)
