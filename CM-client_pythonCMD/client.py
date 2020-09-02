
# --- imports ---
import socketio 
import time

# - global objects - 
sio = socketio.Client()

## --- methods ---

def emit_test():
    sio.emit('updatePatch', 'This is my second websocket-based message ever. Celebrate this!')

@sio.event
def connect():
    print('connected to server')


@sio.event
def updatePatchConfirm(data):
    print('message received:\n \t ', data)


# --- script --- 
sio.connect('http://localhost:3000')
sio.wait()

