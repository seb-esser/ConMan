import asyncio
import json

import websockets


async def route_incoming(websocket, path):
    async for message in websocket:
        print(message)
        payload: dict
        try:
            payload = json.loads(message)
        except:
            Warning("Unable to encode incoming object")
            continue

        # encode sender
        sender: str = payload["SENDER"]

        # encode topic
        topic: str = payload["TOPIC"]

        # encode data
        data = payload["DATA"]

        print("SENDER: {:<12} TOPIC: {:<12} DATA: {} ".format(sender, topic, data))
    websocket.send("confirmed")


async def main():
    url = "127.0.0.1"
    port: int = 6789
    async with websockets.serve(route_incoming, url, port):
        print("STARTED WebSocket Server under {} on port {}".format(url, port))
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
