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
        
    def incorrect_pushed(self):
        self.answers[1] += 1

    def finished_pushed(self):
        confidence = round(min(max((self.answers[0] / sum(self.answers)) - 0.4, 0.0), 0.55) / 0.55, 4)
        topics = pd.read_csv('topics.csv',index_col='topic_name')
        topics.loc[self.topic, 'confidence'] = confidence
        topics.to_csv('topics.csv')
        self.close()

class ChooseTopicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Self Testing")
        self.resize(400, 300)

        self.hbox = QHBoxLayout()

        self.scroll = QScrollArea()
        self.widgetList = QListWidget()
        self.scrollBox = QVBoxLayout()
        self.widgetList.setLayout(self.scrollBox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widgetList)
        
        for topic in self.load_topics():
            item = QListWidgetItem(topic)
            self.widgetList.addItem(item)

        self.widgetList.itemDoubleClicked.connect(self.open_answer_topic)

        self.add_button = QPushButton("Add Topic")
        self.add_button.pressed.connect(self.add_topic)

        self.hbox.addWidget(self.add_button, 1)
        self.hbox.addWidget(self.scroll, 2)

        self.container = QWidget()
        self.container.setLayout(self.hbox)
        self.setCentralWidget(self.container)

    def add_topic(self):
        text, okPressed = QInputDialog.getText(self, "Enter new topic", "New topic:")
        if not okPressed:
            return
        if not text.strip():
            QMessageBox.warning(self, "Input Error", "No topic entered")
        else:
            pd.read_csv('topics.csv', index_col=False)._append({'topic_name': text.strip(), 'confidence': 0.0, 'review_date': getReviewDate(0.0)}, ignore_index=True).set_index('topic_name').to_csv('topics.csv')

    def load_topics(self):
        df = pd.read_csv('topics.csv')
        df.review_date = pd.to_datetime(df.review_date, format='%Y-%m-%d')
        return list(df.loc[df.review_date <= datetime.datetime.today(), 'topic_name'].sample(frac=1))

    def open_answer_topic(self, topic):
        topic = self.widgetList.takeItem(self.widgetList.row(topic)) # Remove widget from list
        self.window = AnswerTopicWindow(topic.text())
        self.window.show()

app = QApplication(sys.argv)
window = ChooseTopicWindow()
window.show()

app.exec()
