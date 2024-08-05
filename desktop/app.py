from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import *
import datetime
import dateutil
import pandas as pd
import sys

def getReviewDate(confidence):
    max_day = 30
    return (datetime.datetime.today() + dateutil.relativedelta.relativedelta(days=1+int(confidence * max_day))).strftime('%Y-%m-%d')

class AnswerTopicWindow(QMainWindow):
    def __init__(self, topic, calling_window):
        super().__init__()
        self.setWindowTitle("Answer topic")
        layout = QHBoxLayout()
        self.answers = [0, 0]
        self.topic = topic
        self.calling_window = calling_window
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
        
    def incorrect_pushed(self):
        self.answers[1] += 1

    def finished_pushed(self):
        confidence = round(min(max((self.answers[0] / sum(self.answers)) - 0.4, 0.0), 0.55) / 0.55, 4)
        topics = pd.read_csv('topics.csv',index_col='topic_name')
        topics.loc[self.topic, 'confidence'] = confidence
        topics.to_csv('topics.csv')
        self.calling_window.finish_topic(self.topic)
        self.close()

class ChooseTopicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        topics = ["Wills","Property","Relax"]
        self.setWindowTitle("Choose today's topic")
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.topicButtons = {}

        for topic in testTopics:
            button = QPushButton(topic)
            button.pressed.connect(lambda t=topic: self.open_answer_topic(t))
            self.topicButtons[topic] = button
            self.vbox.addWidget(button)
        self.widget.setLayout(self.vbox)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        button = QPushButton("Add topic")
        button.pressed.connect(self.add_topic)

        self.hbox.addWidget(button)
        self.hbox.addWidget(self.scroll)
        container = QWidget()
        container.setLayout(self.hbox)

        self.setCentralWidget(container)

    def add_topic(self):
        text, okPressed = QInputDialog.getText(self, "Enter new topic", "New topic:")
        if not okPressed:
            return
        if not text.strip():
            QMessageBox.warning(self, "Input Error", "No topic entered")
        else:
            pd.read_csv('topics.csv', index_col=False)._append({'topic_name': text.strip(), 'confidence': 0.0, 'review_date': getReviewDate(0.0)}, ignore_index=True).set_index('topic_name').to_csv('topics.csv')

    def finish_topic(self, topic):
        self.topicButtons[topic].setParent(None)
        del self.topicButtons[topic]

    def open_answer_topic(self, topic):
        self.window = AnswerTopicWindow(topic, self)
        self.window.show()

app = QApplication(sys.argv)
window = ChooseTopicWindow()
window.show()

app.exec()
