from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QPushButton,
    QMessageBox,
    QGridLayout,
    QWidget,
    QComboBox,
    QLabel,
    QLineEdit,
    QProgressBar,
)
from generate import generate, save
import re
import os


class GeneratorWindow(QMainWindow):
    def __init__(self, main_win):
        super(GeneratorWindow, self).__init__()
        self.main_window = main_win  # parent main window
        self.main_widget = QWidget()  # main widget in central of frame
        self.model_combo_box = QComboBox()  # model choose combo box
        self.start_seq_combo_box = QComboBox()
        self.model_type = "lofi"
        self.start_sequence = "The Stranger Things Theme"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Generate")
        self.setFixedSize(480, 200)
        self.model_combo_box.addItems(["Classical", "Nintendo", "Lofi"])
        self.model_combo_box.currentIndexChanged.connect(self.model_change)
        layout = QGridLayout()
        layout.addWidget(QLabel("Pick the genre:"), 0, 0)
        layout.addWidget(self.model_combo_box, 0, 1)

        self.start_seq_combo_box.addItems(
            [
                "The Stranger Things Theme",
                "Africa by Toto",
                "Clocks by Coldplay",
                "Dancing Queen by Abba",
                "Don't Start Now by Dua Lipa",
            ]
        )
        self.start_seq_combo_box.currentIndexChanged.connect(self.choose_input)
        layout.addWidget(QLabel("Pick a song to start with:"), 1, 0)
        layout.addWidget(self.start_seq_combo_box, 1, 1)

        self.file_name = QLineEdit("new_song")
        layout.addWidget(QLabel("Your song's name:"), 2, 0)
        layout.addWidget(self.file_name, 2, 1)

        self.generate_button = QPushButton("Generate", self)
        self.generate_button.clicked.connect(self.generate_procedure)
        layout.addWidget(self.generate_button, 3, 0, 2, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar, 4, 0, 2, 2)

        self.main_widget.setLayout(layout)

        self.setCentralWidget(self.main_widget)
        self.center()

    def model_change(self):
        self.model_type = self.model_combo_box.currentText().lower()

    def choose_input(self):
        self.start_sequence = self.start_seq_combo_box.currentText()

    def generate_procedure(self):  
        self.generate_button.setText("Generating...")
        self.generate_button.repaint()
        self.progress_bar.show()
        self.progress_bar.repaint()

        filename = re.sub(r'\W', '', self.file_name.text()) + ".mid"
        path = os.getcwd() + "/lib/" + filename

        for cur_progress in generate(self.model_type, self.start_sequence, progress=True):
            self.progress_bar.setValue(cur_progress)
            self.progress_bar.repaint()

        save(path)

        self.generate_button.setText("Generate")
        self.generate_button.repaint()
        self.progress_bar.hide()

        QMessageBox.information(
            self,
            "Success",
            "Your file has been saved to<br />{}".format(path)
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Window Close",
            "Are you sure you want to return to the main window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.main_window.show()
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
