import asyncio
import socketio

sio = socketio.AsyncClient()


@sio.event
async def connect():
    print('connected to server')


@sio.event
async def disconnect():
    print('disconnected from server')


@sio.event
def hello(a, b, c):
    print(a, b, c)


@sio.on("UserConnected")
async def new_user(data):
    print(data)


async def start_server():
    await sio.connect('http://localhost:5000', wait_timeout=5, namespaces=["/"])
    await sio.wait()


if __name__ == '__main__':
    asyncio.run(start_server())
