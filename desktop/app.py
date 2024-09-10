from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import *
import datetime
import dateutil
import pandas as pd
import os
import sys

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'studio.lukesoft.study.spacedrecall.1-0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

basedir = os.path.dirname(__file__)
TOPICS = os.path.join(basedir, 'data', 'topics.csv')
DEFAULT_TOPIC_COLUMNS = {
    'confidence': 0.0,
    'review_date': datetime.datetime.today().strftime('%Y-%m-%d'),
    'last_correct': 0.0,
    'last_answered': 0.0
}
if not os.path.exists(TOPICS):
    os.makedirs(os.path.dirname(TOPICS), exist_ok=True)
    with open(TOPICS,'w') as data:
        data.write(f'topic_name,{",".join(DEFAULT_TOPIC_COLUMNS.keys())}')

def getReviewDate(confidence):
    max_day = 30
    return (datetime.datetime.today() + dateutil.relativedelta.relativedelta(days=1+int(confidence * max_day))).strftime('%Y-%m-%d')

class AnswerTopicWindow(QMainWindow):
    def __init__(self, topic):
        super().__init__()
        self.setWindowTitle(f"Answering {topic}")
        layout = QVBoxLayout()
        grid = QGridLayout()
        self.answers = [0, 0]
        self.topic = topic
        topic_label = QLabel(topic)
        correct_button = QPushButton("Correct")
        incorrect_button = QPushButton("Incorrect")
        finished_button = QPushButton("Finished")

        correct_button.clicked.connect(self.correct_pushed)        
        incorrect_button.clicked.connect(self.incorrect_pushed)        
        finished_button.clicked.connect(self.finished_pushed)

        self.correct_label = QLabel("Correct: 0")
        self.incorrect_label = QLabel("Incorrect: 0")

        grid.addWidget(correct_button, 0, 0)
        grid.addWidget(incorrect_button, 0, 1)
        grid.addWidget(finished_button, 0, 2)
        grid.addWidget(self.correct_label, 1, 0)
        grid.addWidget(self.incorrect_label, 1, 1)
        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        layout.addWidget(topic_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(grid_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def correct_pushed(self):
        self.answers[0] += 1
        self.correct_label.setText(f"Correct: {self.answers[0]}")
        
    def incorrect_pushed(self):
        self.answers[1] += 1
        self.incorrect_label.setText(f"Incorrect: {self.answers[1]}")

    def finished_pushed(self):
        confidence = 0 if sum(self.answers) == 0 else round(min(max((self.answers[0] / sum(self.answers)) - 0.4, 0.0), 0.55) / 0.55, 4)
        topics = pd.read_csv(TOPICS,index_col='topic_name')
        for col, default in DEFAULT_TOPIC_COLUMNS.items():
            if col not in topics.columns:
                topics[col] = default
        topics.loc[self.topic, 'confidence'] = confidence
        topics.loc[self.topic, 'review_date'] = getReviewDate(confidence)
        topics.loc[self.topic, 'last_correct'] = self.answers[0]
        topics.loc[self.topic, 'last_answered'] = sum(self.answers)
        topics.to_csv(TOPICS)
        self.close()


class ChooseTopicWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Self Testing")
        self.resize(400, 300)

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.topics_list = self.load_topics()

        self.scroll = QScrollArea()
        self.widgetList = QListWidget()
        self.scrollBox = QVBoxLayout()
        self.widgetList.setLayout(self.scrollBox)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widgetList)
        
        self.add_button = QPushButton("Add Topic")
        self.add_button.pressed.connect(self.add_topic)

        self.search_bar = QLineEdit("")
        self.search_bar.textChanged.connect(self.update_topics)

        self.update_topics()
        self.widgetList.itemDoubleClicked.connect(self.open_answer_topic)
        
        self.inner_container = QWidget()
        self.vbox.addWidget(self.add_button, 1)
        self.vbox.addWidget(self.search_bar, 2)
        self.inner_container.setLayout(self.vbox)
        self.hbox.addWidget(self.inner_container, 1)
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
            pd.read_csv(TOPICS, index_col=False)._append({'topic_name': text.strip(), 'confidence': 0.0, 'review_date': getReviewDate(0.0), 'last_correct': 0.0, 'last_answered': 0.0}, ignore_index=True).set_index('topic_name').to_csv(TOPICS)

    def load_topics(self):
        df = pd.read_csv(TOPICS)
        df.review_date = pd.to_datetime(df.review_date, format='%Y-%m-%d')
        for col, default in DEFAULT_TOPIC_COLUMNS.items():
            if col not in df.columns:
                df[col] = default
        return [f"{row.topic_name} (Last attempt: {int(row.last_correct)}/{int(row.last_answered)})" for _, row in df.loc[df.review_date <= datetime.datetime.today(), ['topic_name','last_correct','last_answered']].sample(frac=1).iterrows()]

    def update_topics(self):
        self.widgetList.clear()
        for topic in self.topics_list:
            if not (self.search_bar.text() == "" or self.search_bar.text() in topic.split("(Last attempt: ")[0].strip()):
                continue
            item = QListWidgetItem(topic)
            self.widgetList.addItem(item)

    def open_answer_topic(self, topic):
        topic_label = self.widgetList.takeItem(self.widgetList.row(topic)) # Remove widget from list
        topic_name = topic_label.text().split("(Last attempt: ")[0].strip()
        self.topics_list.remove(topic_label.text())
        self.window = AnswerTopicWindow(topic_name)
        self.window.show()

app = QApplication(sys.argv)
app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'icons', 'study.ico')))
window = ChooseTopicWindow()
window.show()

app.exec()
