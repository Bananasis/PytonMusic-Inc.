import sys

from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QLabel, QApplication, QVBoxLayout, QWidget,
)


class AboutWindow(QMainWindow):
    def __init__(self, main_win):
        super(AboutWindow, self).__init__()
        self.main_window = main_win  # parent main window
        self.setStyleSheet(
            "* {color: qlineargradient(spread:pad, x1:0 y1:0, x2:1 y2:0, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));"
            "background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 magenta, stop:1 lightblue);}")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("About")
        self.setFixedSize(550, 190)
        layout = QVBoxLayout()
        about_text = QLabel(
            "Here it is. In your hands you have music generator using neural network."
            "\nWith enough midi files you can create basically any kind of song."
            "\nFor more details and instruction visit our github by clicking this link: ",
            self)
        about_text.move(10, 20)

        link = QLabel()
        link.setText('''<a href='https://github.com/Bananasis/PytonMusic-Inc.'>PytonMusic-Inc</a>''')
        link.setOpenExternalLinks(True)

        authors_text = QLabel("by: Dominika Szydło, Patryk Majewski, Ivan Feofilaktov and Gabriel Wechta.")

        layout.addWidget(about_text)
        layout.addWidget(link)
        layout.addWidget(authors_text)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        main_widget.adjustSize()
        # self.about_text.adjustSize()

        self.setCentralWidget(main_widget)
        self.center()

    def closeEvent(self, event):
        self.main_window.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AboutWindow(QMainWindow())
    win.show()
    sys.exit(app.exec_())
