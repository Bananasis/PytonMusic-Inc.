import os
import pygame
import threading
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, \
    QPushButton, QMessageBox, QGridLayout, QWidget, QLabel, QListWidget, QListWidgetItem
from PyQt5 import QtCore

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if not os.path.exists(lib_dir):
    os.makedirs(lib_dir)

class LibraryWindow(QMainWindow):
    def __init__(self, main_win):
        super(LibraryWindow, self).__init__()
        self.main_window = main_win
        self.main_widget = QWidget()
        self.to_play = None
        self.stop_playing = False
        freq = 44100
        bitsize = -16
        channels = 2
        buffer = 1024
        pygame.mixer.init(freq, bitsize, channels, buffer)
        pygame.mixer.music.set_volume(1.0)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Library')
        self.setFixedSize(480, 300)
        layout = QGridLayout()
        self.file_list = QListWidget()
        self.file_list.resize(400, 240)
        for filename in os.listdir(lib_dir):
            if filename.endswith('.mid'):
                item = QListWidgetItem(filename)
                self.file_list.addItem(item)
        self.file_list.itemSelectionChanged.connect(self.file_chosen)
        layout.addWidget(self.file_list, 0, 0, 5, 2)
        play_button = QPushButton('Play!', self)
        play_button.clicked.connect(self.play)
        layout.addWidget(play_button, 5, 0)
        stop_button = QPushButton('Stop', self)
        stop_button.clicked.connect(self.stop)
        layout.addWidget(stop_button, 5, 1)
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)
        self.center()

    def stop(self):
        self.stop_playing = True

    def play(self):
        if self.to_play is None:
            QMessageBox.critical(self, 'Error', 'No file selected!', QMessageBox.Ok)
        else:
            x = threading.Thread(target=self.play_audio, args=())
            x.start()

    def play_audio(self):
        clock = pygame.time.Clock()
        pygame.mixer.music.load(os.path.join(lib_dir, self.to_play))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and not self.stop_playing:
            clock.tick(30)
        pygame.mixer.music.stop()
        self.stop_playing = False

    def file_chosen(self):
        self.to_play = self.file_list.selectedItems()[0].text()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to return to the main window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.stop_playing = True
            self.main_window.show()
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
