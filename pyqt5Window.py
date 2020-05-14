from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QMainWindow, QStatusBar, QToolBar, QDesktopWidget, \
    QVBoxLayout, QPushButton, QFileDialog, QMessageBox
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.wind = None

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
        up_layout.addWidget(title)

        gen_button = QPushButton('Generate', self)
        gen_button.clicked.connect(self.init_generator_window)
        down_layout.addWidget(gen_button)

        lib_button = QPushButton('Library', self)
        # lib_button.clicked.connect(self.init_library_window)
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
        self.wind = GeneratorWindow()
        self.wind.show()
        self.hide()

    # def init_library_window(self):
    #     self.wind = LibraryWindow()
    #     self.wind.show()
    #     self.hide()
    #
    # def init_example_window(self):
    #     self.wind = ExampleWindow()
    #     self.wind.show()
    #     self.hide()


class GeneratorWindow(QMainWindow):
    def __init__(self):
        super(GeneratorWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gdy pytają o pochodzenie, milczę.")
        self.setFixedSize(880, 680)
        choose_dir_button = QPushButton("Choose button", self)
        choose_dir_button.clicked.connect(self.choose)
        self.setCentralWidget(choose_dir_button)
        self.center()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            win.show()
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def choose(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
