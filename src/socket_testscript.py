import asyncio
import socketio

sio = socketio.AsyncClient(logger=True, engineio_logger=True)


@sio.event
async def connect():
    print('connected to server')


@sio.event
async def disconnect():
    print('disconnected from server')


@sio.event
def hello(a):
    print(a)


async def start_server():

    print("[CLIENT] trying to connect...")
    await sio.connect('http://localhost:5000')
    print("[CLIENT] connected.")
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(start_server())
    #

