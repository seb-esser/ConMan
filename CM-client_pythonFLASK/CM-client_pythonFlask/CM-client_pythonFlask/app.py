"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask
import socketio
import os

app = Flask(__name__)
app.config['DEBUG'] = False

sio = socketio.Client()

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    
    # frontend message
    return "Hello World!"

@app.route('/emit-test')
def emitTest(): 
    sio.emit('updatePatch', 'This is my first websocket-based message ever. Celebrate this!')
    return "test the emit function"

# --- catch socket events ---
@sio.event
def connect():
    print('#Socket-Event: \t connected to server')

@sio.event
def updatePatchConfirm(data):
    print('message received:\n \t ', data)

@sio.event
def disconnect():
    print('#Socket-Event: \t disconnected from server')


# --- main function --- 
if __name__ == '__main__':
    
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5000'))
    #except ValueError:
    #    PORT = 5000

    # connect socket
    print('trying to connect socket to CM server...')
    sio.connect('http://localhost:3000')
    print('connected to CM server as {}'.format(sio.sid))

    app.run(port=4000, threaded=True)


