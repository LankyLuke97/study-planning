from PyQt6.QtWidgets import *

import sys


class AnswerTopicWindow(QMainWindow):
    pass

class ChooseTopicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        testTopics = ["Wills","Proprty","Relax"]
        self.setWindowTitle("Choose today's topic")
        layout = QStackedLayout()
        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Study App")
        self.label = QLabel()

        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)

        container =QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

app = QApplication(sys.argv)

window = ChooseTopicWindow()
window.show()

app.exec()
