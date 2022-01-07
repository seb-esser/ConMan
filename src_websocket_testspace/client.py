import asyncio
import websockets


async def hello():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        d = {"SENDER": "client1",
             "TOPIC": "main_topic",
             "DATA": {
                 "a": 1,
                 "b": 2,
                 "c": True
             }}

        await websocket.send(str(d))
        await websocket.recv()


asyncio.run(hello())
