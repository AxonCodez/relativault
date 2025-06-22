from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load questions from JSON
with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r') as f:
    questions = json.load(f)

@app.route('/')
def index():
    session['streak'] = session.get('streak', 0)
    return render_template('index.html', streak=session['streak'])

@app.route('/questions')
def show_questions():
    session['start_time'] = time.time()  # Start the timer
    session['answers'] = {}              # Store user answers
    return render_template('questions.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit_answers():
    end_time = time.time()
    start_time = session.get('start_time', end_time)
    total_time = int(end_time - start_time)

    user_answers = request.form.to_dict()
    correct = 0
    streak = 0
    max_streak = 0

    for qid, answer in user_answers.items():
        qid = int(qid.replace('q', ''))
        if qid <= len(questions):
            question = questions[qid-1]
            if int(answer) == question['answer']:
                correct += 1
                streak += 1
                if streak > max_streak:
                    max_streak = streak
            else:
                streak = 0

    session['streak'] = max_streak
    return render_template('results.html', 
                          correct=correct, 
                          total=len(questions),
                          time=total_time,
                          streak=max_streak)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        try:
            new_question = {
                "id": len(questions) + 1,
                "text": request.form['question'],
                "options": [
                    request.form['opt1'],
                    request.form['opt2'],
                    request.form['opt3'],
                    request.form['opt4']
                ],
                "answer": int(request.form['correct']),
                "time_limit": 0,  # Not used in this flow
                "category": request.form['category']
            }
            questions.append(new_question)
            with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'w') as f:
                json.dump(questions, f, indent=2)
        except Exception as e:
            print(f"Error: {e}")
            return "Bad Request", 400
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)
