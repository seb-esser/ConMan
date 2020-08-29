
# --- imports ---
import socketio 
import time

## --- methods ---
#class Connector(socketio.Namespace): 
#    sio = socketio.Client()

#    def __init__(self): 
#        sio.connect('http://localhost:3000')
#        pass

#    @sio.on('connect')
#    def connect_handler():        
#        print("I'm connected!")

#    @sio.event
#    def my_event(data):
#    print('Received data: ', data)


## --- script --- 
#connector = Connector

sio = socketio.Client(engineio_logger=True)
start_timer = None


def send_ping():
    global start_timer
    start_timer = time.time()
    sio.emit('ping_from_client')


@sio.event
def connect():
    print('connected to server')
    send_ping()


@sio.event
def pong_from_server():
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    sio.sleep(1)
    send_ping()


# --- script --- 
sio.connect('http://localhost:3000')

