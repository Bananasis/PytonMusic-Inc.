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
    QProgressBar, QRadioButton, QHBoxLayout,
)

import re
import os
import sys

project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.join(project_path, "net1"), os.path.join(project_path, "net2")])
import net1_generate as net1
import net2_generate as net2


class GeneratorWindow(QMainWindow):
    def __init__(self, main_win):
        super(GeneratorWindow, self).__init__()
        self.main_window = main_win  # parent main window
        self.main_widget = QWidget()  # main widget in central of frame
        self.notes_radio_button = QRadioButton("Notes")
        self.bin_vec_radio_button = QRadioButton("Bin Vec")
        self.model_combo_box = QComboBox()  # model choose combo box
        self.start_seq_combo_box = QComboBox()
        self.model_type = "lofi"
        self.start_sequence = "The Stranger Things Theme"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Generate")
        self.setFixedSize(480, 240)
        layout = QGridLayout()
        layout_holder = QHBoxLayout()

        self.notes_radio_button.setChecked(True)
        self.bin_vec_radio_button.setChecked(False)

        layout_holder.addWidget(self.notes_radio_button)
        layout_holder.addWidget(self.bin_vec_radio_button)

        holder = QWidget()
        holder.setLayout(layout_holder)

        layout.addWidget(QLabel("Pick architecture:"), 0, 0)
        layout.addWidget(holder, 0, 1)

        self.model_combo_box.addItems(["Classical", "Nintendo", "Ps1"])
        self.model_combo_box.currentIndexChanged.connect(self.model_change)

        layout.addWidget(QLabel("Pick the genre:"), 1, 0)
        layout.addWidget(self.model_combo_box, 1, 1)

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
        layout.addWidget(QLabel("Pick a song to start with:"), 2, 0)
        layout.addWidget(self.start_seq_combo_box, 2, 1)

        self.file_name = QLineEdit("new_song")
        layout.addWidget(QLabel("Your song's name:"), 3, 0)
        layout.addWidget(self.file_name, 3, 1)

        self.generate_button = QPushButton("Generate", self)
        self.generate_button.clicked.connect(self.generate_procedure)
        layout.addWidget(self.generate_button, 4, 0, 2, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar, 5, 0, 2, 2)

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
        
        generate = net1.generate if True else net2.generate #TODO
        filename = re.sub(r'\W', '', self.file_name.text()) + ".mid"
        path = project_path + "/lib/" + filename

        for cur_progress in generate(self.model_type, self.start_sequence, filename):
            self.progress_bar.setValue(cur_progress)
            self.progress_bar.repaint()

        self.generate_button.setText("Generate")
        self.generate_button.repaint()
        self.progress_bar.hide()

        QMessageBox.information(
            self,
            "Success",
            f"Your file has been saved to<br />{path}"
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
