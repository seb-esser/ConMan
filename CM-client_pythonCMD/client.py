
# --- imports ---
import socketio 
import time

# --- methods ---



# --- script --- 
sio = socketio.Client()

@sio.event
def my_event(sid, data):
    # handle the message
    print(data)

# connect the socket
print('... connecting Client ... ')

connect_res = sio.connect('http://localhost:3000')
print('my user id is: \t', sio.sid)

# wait some time before disconnecting

print('Emitting a test message... ')
sio.emit('updatePatch', {'foo': 'bar'})

time.sleep(2)

sio.on('updatePatchConfirm', my_event)
  

# disconnect
sio.disconnect(); 

