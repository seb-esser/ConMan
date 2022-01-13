import json

from flask import Flask, request, jsonify, render_template
from flask_socketio import send, emit, SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)  # , async_mode='eventlet')
messages = []


@app.route('/')
def render_landing_page():
    return render_template("index.html")


@app.route('/api/ReportTransaction', methods=["POST"])
def report_transaction():
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


@socketio.on('message')
def handle_message(data):
    print('[WS] received message: ' + data)


if __name__ == "__main__":
    # app.run()
    socketio.run(app)

    # In order to run this server properly, the following packages are required:
    # - Flask_SocketIO (pip install flask_socketio)
    # - eventlet (pip install eventlet)
    # Debug or run config: `python run.py` (standard python config in pycharm)

