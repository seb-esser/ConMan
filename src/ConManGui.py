import asyncio
import sys
from functools import cached_property

from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from asyncqt import QEventLoop

import socketio


class Client(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.sio = socketio.AsyncClient()

        self.connected = pyqtSignal()
        self.disconnected = pyqtSignal()
        self.error_occurred = pyqtSignal(object, name="errorOccurred")
        self.data_changed = pyqtSignal(str, name="dataChanged")

        # register events and corresponding callback functions
        self.sio.on("connect", self._handle_connect, namespace=None)
        self.sio.on("connect_error", self._handle_connect_error, namespace=None)
        self.sio.on("disconnect", self._handle_disconnect, namespace=None)
        self.sio.on("UserConnected", self._user_connected, namespace=None)

    # @cached_property
    # def sio(self):
    #     return socketio.AsyncClient()

    async def start(self):
        await self.sio.connect(url="http://localhost:5000", wait_timeout=5, namespaces=["/"])

    def _handle_connect(self):
        self.connected.emit()

    def _handle_disconnect(self):
        self.disconnect.emit()

    def _handle_connect_error(self, data):
        self.error_occurred.emit(data)

    def _user_connected(self, data):
        print(data)


class View(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel(alignment=Qt.AlignCenter)
        self.setCentralWidget(self.label)
        self.resize(640, 480)

    def update_data(self, message):
        self.label.setText(message)


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    view = View()
    view.show()

    client = Client()
    # client.data_changed.connect(view.update_data)

    with loop:
        asyncio.ensure_future(client.start(), loop=loop)
        loop.run_forever()


if __name__ == "__main__":
    main()
