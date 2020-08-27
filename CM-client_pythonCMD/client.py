
# --- imports ---
import socketio 
import time

# --- script --- 
sio = socketio.Client()

# connect the socket
print('... connecting Client ... ')

connect_res = sio.connect('http://localhost:3000')
print('my user id is: \t', sio.sid)

# wait some time before disconnecting
time.sleep(3)

# disconnect
sio.disconnect(); 

