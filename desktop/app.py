from PyQt6.QtWidgets import *
import pandas as pd
import sys


class AnswerTopicWindow(QMainWindow):
    def __init__(self, topic):
        super().__init__()
        self.setWindowTitle("Answer topic")
        layout = QHBoxLayout()
        self.answers = [0, 0]
        self.topic = topic
        correct_button = QPushButton("Correct")
        incorrect_button = QPushButton("Incorrect")
        finished_button = QPushButton("Finished")

        correct_button.clicked.connect(self.correct_pushed)        
        incorrect_button.clicked.connect(self.incorrect_pushed)        
        finished_button.clicked.connect(self.finished_pushed)        

        layout.addWidget(correct_button)
        layout.addWidget(incorrect_button)
        layout.addWidget(finished_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def correct_pushed(self):
        self.answers[0] += 1
        print("adding 1 correct")
        
    def incorrect_pushed(self):
        self.answers[1] += 1
        print("adding 1 wrong")

    def finished_pushed(self):
        print("finished")
        confidence = round(min(max((self.answers[0] / sum(self.answers)) - 0.4, 0.0), 0.55) / 0.55, 4)
        print("Confidence: {}".format(confidence))
        topics = pd.read_csv('topics.csv',index_col='topic_name')
        topics.loc[self.topic, 'confidence'] = confidence
        topics.to_csv('topics.csv')

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

window = AnswerTopicWindow('wills')
window.show()

app.exec()
