# imports 
# import websockets as ws
from websocket import create_connection
import asyncio 

# classes
class CM_connector:
    # vars
    server_address = "http://localhost"
    port = 4000

    # constructor
    def __init__(self):
        self.data = []
        pass

    # methods
    
    
async def connect():
    print('connecting... ')
    uri = 'ws://localhost:3000'

    async with ws.connect(uri) as websocket:
       print('say hello')
       result = await websocket.send('connection')  
       print(result)

# script

print('-- CM client -- ')
# asyncio.get_event_loop().run_until_complete(connect())
ws = create_connection("ws://localhost:3000")
print ("Sending 'Hello, World'...")
ws.send("Hello, World")
print ("Sent")

