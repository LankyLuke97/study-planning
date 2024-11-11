import datetime
import dateutil
import os
import pandas as pd
import sys

def newStudy(csv, today):
    tomorrow = (today + dateutil.relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d')
    currentDB = pd.read_csv(csv,index_col=0,sep='|')
    newQuestions = {col: [] for col in currentDB.columns}
    while True:
        inp = input('Do you have more questions to add? ').lower()
        if inp.startswith('n'):
            break
        if not inp.startswith('y'):
            continue
        question = ''
        answer = ''
        tags = ''
        while True:
            question = input('Please write question: ')
            if input('Are you happy with the question? ').lower().startswith('y'):
                newQuestions['question'].append(question)
                break
        while True:
            answer = input('Please supply answer: ')
            if input('Are you happy with the answer? ').lower().startswith('y'):
                newQuestions['answer'].append(answer)
                break
        while True:
            tags = input('Please supply a comma-separated list of tags: ')
            if input('Are you happy with the tags? ').lower().startswith('y'):
                newQuestions['tags'].append(tags)
                break
        with open(csv,'a') as db:
            db.write(f"Question: {question} | Answer: {answer}\n")
    newQuestions['review_date'] = [tomorrow] * len(newQuestions['question'])
    newQuestions['review_box'] = [0] * len(newQuestions['question'])
    newQuestions['hint'] = [''] * len(newQuestions['question'])
    newDB = pd.concat([currentDB, pd.DataFrame(newQuestions)], ignore_index=True)
    newDB.to_csv(csv,sep='|')

def review(csv, date_threshold, confidence_level=-1):
    questions = pd.read_csv(csv,index_col=0,sep='|')
    questions.fillna(' ', inplace=True)
    questions['review_date'] = pd.to_datetime(questions['review_date'], format='%Y-%m-%d')
    questions['hint'] = questions['hint'].astype(str)
    todays = None
    if confidence_level>=0:
        todays = questions.loc[questions['review_box'] <= confidence_level, :].sample(frac=1)
    else:
        todays = questions.loc[questions['review_date'] <= date_threshold, :].sample(frac=1)
    print('Spread of questions:')
    print(questions['review_date'].value_counts().sort_index(ascending=True))
    print('There are {} questions to answer today.'.format(len(todays)))
    correct = 0
    total_questions = len(todays)
    progress = 0
    nextDates = [dateutil.relativedelta.relativedelta(days=1), dateutil.relativedelta.relativedelta(days=3), dateutil.relativedelta.relativedelta(weeks=1), dateutil.relativedelta.relativedelta(weeks=2), dateutil.relativedelta.relativedelta(months=1)]
    for idx, row in todays.iterrows():
        progress += 1
        if "i am done" in input(f"Question {progress}/{total_questions}: {row['question']} {row['hint']}\n").lower():
            print("Finishing studying for now.")
            break
        print(f"The correct answer was: {row['answer']}")
        newBox = row['review_box']
        if input('Were you correct? ').lower().startswith('y'):
            newBox = int(min(row['review_box'] + 1, 4))
            row['hint'] = ' '
            correct += 1
        else:
            if int(row['review_box']) == 0:
                hint = input('Would you like to add a hint? ')
                if not hint.lower().startswith('no'):
                    if len(hint) != 0:
                        row['hint'] = hint
            newBox = int(max(0, row['review_box'] - 1))
        row['review_date'] = (datetime.datetime.today() + nextDates[newBox]).strftime('%Y-%m-%d')
        row['review_box'] = newBox
        questions.iloc[idx] = row
        questions.to_csv(csv,sep='|')
    if total_questions > 0:
        questions.to_csv(csv,sep='|')
        print("You got {} out of {} correct".format(correct, progress - 1 if progress < total_questions else total_questions))

if __name__=='__main__':
    today = datetime.datetime.today()
    
    topic = input("What would you like to study? ").lower()
    if not os.path.exists(f"{topic}.csv"):
        if input(f"{topic} doesn't yet exist - would you like to start a new file? ").lower().startswith('y'):
            with open(f"{topic}.csv",'w') as questions:
                questions.write('|review_date|question|answer|review_box|tags')
        else:
            sys.exit() 

    newStudy(f"{topic}.csv", today)
    review_input = input('Would you like to review questions for today? ').lower()
    if review_input.startswith('y'):
        questions = review(f"{topic}.csv", today)
    else:
        try:
            confidence = int(review_input)
            questions = review(f"{topic}.csv", today, confidence_level=confidence)
        except:
            pass
