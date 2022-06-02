from PyQt5.QtWidgets import (QAction, QApplication, QFormLayout, QGroupBox,
                             QLabel, QPushButton, QVBoxLayout, QWidget,
                             QMainWindow, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QThread

import websocket


class ListenWebsocket(QThread):
    def __init__(self, parent=None):
        super(ListenWebsocket, self).__init__(parent)

        websocket.enableTrace(True)

        self.WS = websocket.WebSocketApp("ws://localhost:5000/", on_message=self.on_message)

    def run(self):
        self.WS.run_forever()

    def on_message(self, message):
        print(message)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_ui()
        self.create_menu()

        # add socket thread
        self.thread = ListenWebsocket()
        self.thread.start()

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

    mainWindow.show()
    application.exec()
