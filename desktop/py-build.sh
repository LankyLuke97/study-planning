mv data/topics.csv ../topics.csv

APP_NAME="Spaced Recall ${1}"
export APP_NAME
pyinstaller spaced_recall.spec

mv ../topics.csv data/topics.csv
