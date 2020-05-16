from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, \
    QPushButton, QFileDialog, QMessageBox, QGridLayout, QWidget, QComboBox, QLabel


class GeneratorWindow(QMainWindow):
    def __init__(self, main_win):
        super(GeneratorWindow, self).__init__()
        self.main_window = main_win  # parent main window
        self.main_widget = QWidget()  # main widget in central of frame
        self.model_combo_box = QComboBox()  # model choose combo box
        # self.base_combo_box = QComboBox()  # base choose combo box
        self.model_type = "Classical"
        # self.base_type = "Mozart V5"
        self.input_path = None
        self.output_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Generate")
        self.setFixedSize(480, 300)
        self.model_combo_box.addItems(["Classical", "House", "8-bit"])
        self.model_combo_box.currentIndexChanged.connect(self.model_change)
        layout = QGridLayout()
        layout.addWidget(QLabel("Pick music genre:"), 0, 0)
        layout.addWidget(self.model_combo_box, 0, 1)

        choose_input_path_button = QPushButton("Choose input file", self)
        choose_input_path_button.clicked.connect(self.choose_input)
        layout.addWidget(QLabel("Pick music input base:"), 1, 0)
        layout.addWidget(choose_input_path_button, 1, 1)

        choose_output_path_button = QPushButton("Choose output directory", self)
        choose_output_path_button.clicked.connect(self.choose_output)
        layout.addWidget(QLabel("Pick output file location:"), 2, 0)
        layout.addWidget(choose_output_path_button, 2, 1)

        generate_button = QPushButton("Generate", self)
        generate_button.clicked.connect(self.generate_procedure)
        layout.addWidget(generate_button, 3, 0, 2, 2)

        self.main_widget.setLayout(layout)

        self.setCentralWidget(self.main_widget)
        self.center()

    def model_change(self):
        self.model_type = self.model_combo_box.currentText()
        # TODO tutaj przydałoby się zrobić path do modelu, albo w generate.py. Jak wolisz.
        # print(self.model_type)

    def choose_input(self):
        self.input_path = str(QFileDialog.getOpenFileName(self, "Select input file")).split()[0][2:-2]
        # print(self.input_path)

    def choose_output(self):
        self.output_path = str(QFileDialog.getExistingDirectory(self, "Select output directory"))
        print(self.output_path)

    def generate_procedure(self):  # TODO to się dzieje po naciśnięciu "Generate". Wszytskie niezbędne dane masz w w polach self.
        # if self.input_path is None or self.output_path is None:
        #     pass

        # if not self.input_path.endswith(".mid") and not self.input_path.endswith(".midi"):
        #     msg = QMessageBox()
        #     msg.setIcon(QMessageBox.Information)
        #
        #     msg.setText("You should choose MIDI ot MID extension.")
        #     msg.setWindowTitle("Wrong input!")
        #     msg.show()
        #
        pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to return to main window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

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
