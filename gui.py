import sys
from gui_generate_window import GeneratorWindow
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QDesktopWidget, \
    QVBoxLayout, QPushButton
from PyQt5 import QtCore


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.generate_window = None

    def init_ui(self):
        self.setWindowTitle("Python NN Music Generator")
        self.put_buttons()
        self.setFixedSize(640, 480)
        self.center()
        self.show()

    def put_buttons(self):
        up_wid = QWidget(self)
        down_wid = QWidget(self)
        up_layout = QVBoxLayout()
        down_layout = QVBoxLayout()
        main_widget = QWidget(self)
        main_layout = QVBoxLayout()
        title = QLabel("<h1> Generator Muzyki - Zawiadaka 6502! </h1>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        up_layout.addWidget(title)

        gen_button = QPushButton('Generate', self)
        gen_button.clicked.connect(self.init_generator_window)
        down_layout.addWidget(gen_button)

        lib_button = QPushButton('Library', self)
        lib_button.clicked.connect(self.init_library_window)
        down_layout.addWidget(lib_button)

        exa_button = QPushButton('Example', self)
        # exa_button.clicked.connect(self.init_example_window)
        down_layout.addWidget(exa_button)

        up_wid.setLayout(up_layout)
        down_wid.setLayout(down_layout)
        main_layout.addWidget(up_wid)
        main_layout.addWidget(down_wid)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_generator_window(self):
        self.generate_window = GeneratorWindow(self)
        self.generate_window.show()
        self.hide()

    def init_library_window(self):
        self.wind = LibraryWindow()
        self.wind.show()
        self.hide()
    #
    # def init_example_window(self):
    #     self.wind = ExampleWindow()
    #     self.wind.show()
    #     self.hide()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
