from flask import Flask, render_template
from flask_socketio import SocketIO, emit


# basic Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)


def on_connect(auth):
    print('new connection: {}'.format(auth))
    emit('my response', {'data': 'Connected'})


def handle_my_custom_event(data):
    print('received args: {}'.format(data))
    emit('response', data, broadcast=True)


# register events
socketio.on_event('event', handle_my_custom_event, namespace='/')
socketio.on_event('connect', on_connect, namespace='/')


# main
if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000)

