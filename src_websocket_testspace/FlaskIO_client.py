import asyncio
import socketio

sio = socketio.AsyncClient()


@sio.event
def connect():
    print('Connected. ')


@sio.event
def disconnect():
    print('Disconnected. ')


@sio.event
def response(data):
    print("Received an event: {}".format(data))


async def main():
    await sio.connect('http://localhost:5000')
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())



