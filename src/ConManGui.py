import socketio

from PyQt5.QtWidgets import (QAction, QApplication, QFormLayout, QGroupBox,
                             QLabel, QPushButton, QVBoxLayout, QWidget,
                             QMainWindow, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QThread

sio = socketio.AsyncClient()


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
        addBtn = QPushButton("Add", self)
        commitBtn = QPushButton("Commit", self)
        pushBtn = QPushButton("Push", self)
        pullBtn = QPushButton("Pull", self)

        self._vertical_layout.addWidget(addBtn)
        self._vertical_layout.addWidget(commitBtn)
        self._vertical_layout.addWidget(pushBtn)
        self._vertical_layout.addWidget(pullBtn)

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


# @sio.event
# async def connect():
#     print('connected to server')
#
#
# @sio.event
# async def disconnect():
#     print('disconnected from server')
#
#
# @sio.on("UserConnected")
# async def new_user(data):
#     sid_a = sio.get_sid()
#     sid_b = sio.sid
#     print(sid_a)
#     print(sid_b)
#     print("received message from SID: {} ".format(sid_b))
#     print("message: {}".format(data))
#
#
# async def start_server():
#     await sio.connect('http://localhost:5000', wait_timeout=5, namespaces=["/"])
#     print("my SID is: {}\n".format(sio.sid))
#     await sio.wait()


if __name__ == '__main__':
    application = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()

    # asyncio.run(start_server())

    application.exec()


