from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load questions from JSON
with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r') as f:
    questions = json.load(f)

@app.route('/')
def index():
    session['streak'] = session.get('streak', 0)
    return render_template('index.html', streak=session['streak'])

@app.route('/quiz/<int:qid>')
def quiz(qid):
    if qid < 1 or qid > len(questions):
        return redirect('/')
    session['streak'] = session.get('streak', 0)
    return render_template('quiz.html', question=questions[qid-1])

@app.route('/submit', methods=['POST'])
def submit_answer():
    qid = int(request.form['qid']) - 1
    selected = int(request.form['answer'])
    is_correct = (selected == questions[qid]['answer'])
    if is_correct:
        session['streak'] = session.get('streak', 0) + 1
    else:
        session['streak'] = 0
    next_qid = qid + 2 if qid + 1 < len(questions) else None
    return jsonify({
        "correct": is_correct,
        "streak": session['streak'],
        "next": next_qid
    })

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
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
            "time_limit": int(request.form['time_limit']),
            "category": request.form['category']
        }
        questions.append(new_question)
        with open('api/questions.json', 'w') as f:
            json.dump(questions, f, indent=2)
    return render_template('admin.html')
