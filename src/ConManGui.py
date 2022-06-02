import socketio
from PyQt5.QtWidgets import (QAction, QApplication, QFormLayout, QGroupBox,
                             QLabel, QPushButton, QVBoxLayout, QWidget,
                             QMainWindow, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QThread


class ServerConnection(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.sio = socketio.AsyncClient(reconnection=True, reconnection_attempts=3,
                   reconnection_delay=5, reconnection_delay_max=5, logger=True)

    'thread run function'
    def run(self) -> None:
        self.sio.connect(url="localhost:5000", socketio_path="/", transports="websocket")
        self.sio.on('connect', self.connect, namespace=None)
        self.sio.on('socket_connected', self.socket_connected, namespace=None)
        self.sio.on('connect_error', self.connect_error, namespace=None)
        self.sio.on('/client_Unlock', self.client_unlock_ack, namespace=None)
        self.sio.on('UserConnected', self.userConnected, namespace=None)

    # @sio.on('/client_unlock')
    'custom event from server, on receiving, this socketio thread needs to inform main GUI'
    async def client_unlock_ack(self, data):
            print(data)
            'from here i want to call pyqt GUI main class function'

    async def userConnected(self, data):
        print(data)

    # @sio.event
    'connection established status'
    def connect(self):
        print('Server Connection established!')

    # @sio.on("socket_connected")
    'socket connection status check'
    async def socket_connected(self, message):
        print("Socket Connected!", message)

    # @sio.event
    def connect_error(self, data):
        print('Connection error!', data)

    # @sio.on('disconnect' or 'socket_disconnected')
    def disconnect(self):
        print('Disconnected!')


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_ui()
        self.create_menu()

    def create_ui(self):
        # Create window
        self.setWindowTitle('Event Hub Client')
        self.resize(800, 500)
        self.setMinimumSize(500, 450)
        # Create central widget and layout
        self._central_widget = QWidget()
        self._vertical_layout = QVBoxLayout()
        self._central_widget.setLayout(self._vertical_layout)
        # Set central widget
        self.setCentralWidget(self._central_widget)
        # Vertically center widgets
        self._vertical_layout.addStretch(1)

        # Vertically center widgets
        self._vertical_layout.addStretch(1)

        text_area = QTextEdit()
        self._vertical_layout.addWidget(text_area)

        # Add Copyright
        self.addCopyRight()

    def addCopyRight(self):
        copyRight = QLabel(
            'Copyright © <a href="https://cms.ed.tum.com/">TUM CMS</a> 2022')
        copyRight.setOpenExternalLinks(True)
        self._vertical_layout.addWidget(copyRight, alignment=Qt.AlignCenter)

    def create_menu(self):
        # Create menu bar
        menu_bar = self.menuBar()
        # Add menu items
        file_menu = menu_bar.addMenu('File')
        connect_menu = file_menu.addAction('Connect')
        disconnect_menu = file_menu.addAction('Disconnect')


if __name__ == '__main__':
    application = QApplication([])
    mainWindow = MainWindow()

    con = ServerConnection()
    con.start()

    mainWindow.show()
    application.exec()

