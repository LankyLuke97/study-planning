import datetime
import dateutil
import pandas as pd

def newStudy(csv, today):
    tomorrow = (today + dateutil.relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d')
    lines = open(csv,'r').readlines()
    nextId = 0 if len(lines) == 1 else max([int(line.split(',')[0]) for line in lines[1:]]) + 1 # For consistency, switch to using pandas here
    with open(csv, 'a') as db:
        while True:
            inp = input('Do you have more questions to add? ').lower()
            if inp.startswith('n'):
                break
            if not inp.startswith('y'):
                continue
            question = ''
            answer = ''
            while True:
                question = input('Please write question: ')
                if input('Are you happy with the question? ').lower().startswith('y'):
                    break
            while True:
                answer = input('Please supply answer: ')
                if input('Are you happy with the answer? ').lower().startswith('y'):
                    break
            db.write(f"{nextId}|{tomorrow}|{question}|{answer}|0")
            nextId += 1

def review(csv, date_threshold):
    questions = pd.read_csv(csv,index_col=0,sep='|')
    questions['review_date'] = pd.to_datetime(questions['review_date'], format='%Y-%m-%d')
    todays = questions.loc[questions['review_date'] <= date_threshold, :].sample(frac=1)
    nextDates = [dateutil.relativedelta.relativedelta(days=1), dateutil.relativedelta.relativedelta(days=3), dateutil.relativedelta.relativedelta(weeks=1), dateutil.relativedelta.relativedelta(weeks=2), dateutil.relativedelta.relativedelta(months=1)]
    for _ in range(len(todays)):
        idx, row = next(todays.iterrows())
        input(f"{row.iloc[1]}\n")
        print(f"The correct answer was: {row.iloc[2]}")
        newBox = row.iloc[3]
        if input('Were you correct? ').lower().startswith('y'):
            newBox = min(row.iloc[3] + 1, 4)
        else:
            newBox = max(0, row.iloc[3] - 1)
        questions.iloc[idx] = ((row.iloc[0] + nextDates[newBox]).strftime('%Y-%m-%d'), row.iloc[1], row.iloc[2], newBox)
    questions.to_csv(csv,sep='|')

if __name__=='__main__':
    today = datetime.datetime.today()

    if input('Have you studied something new? ').lower().startswith('y'):
        newStudy('questions.csv', today)

    questions = review('questions.csv', today)
