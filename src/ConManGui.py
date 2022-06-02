from PyQt5.QtWidgets import (QAction, QApplication, QFormLayout, QGroupBox,
                             QLabel, QPushButton, QVBoxLayout, QWidget,
                             QMainWindow, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


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
