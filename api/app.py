from flask import Flask, render_template, request, session, redirect, url_for
import json
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load questions from JSON
with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r') as f:
    questions = json.load(f)

# Subtopics with icons
SUBTOPICS = [
    {"name": "Relativistic Effects", "icon": "⚡"},
    {"name": "Time Dilation", "icon": "⏳"},
    {"name": "Velocity Transformation", "icon": "🔄"},
    {"name": "Relativistic Momentum", "icon": "🚀"},
    {"name": "Lorentz Transformation", "icon": "🔁"},
    {"name": "Twin Paradox", "icon": "👯"},
    {"name": "Space-Time", "icon": "🌌"},
    {"name": "4 Vectors", "icon": "🔢"}
]

def get_subtopic_counts():
    counts = {sub["name"]: 0 for sub in SUBTOPICS}
    for q in questions:
        if q.get("subtopic") in counts:
            counts[q["subtopic"]] += 1
    return counts

@app.route('/')
def index():
    session['streak'] = session.get('streak', 0)
    return render_template('index.html', streak=session['streak'])

@app.route('/subtopics')
def subtopics():
    counts = get_subtopic_counts()
    return render_template('subtopics.html', subtopics=SUBTOPICS, counts=counts)

@app.route('/questions/<subtopic>')
def show_questions_by_subtopic(subtopic):
    normalized = subtopic.replace('-', ' ').lower()
    filtered = [q for q in questions if q.get("subtopic", "").lower().replace('-', ' ') == normalized]
    return render_template('questions_list.html', questions=filtered, subtopic=subtopic.title())

@app.route('/question/<int:qid>')
def question_detail(qid):
    question = next((q for q in questions if q["id"] == qid), None)
    if not question:
        return "Question not found", 404
    return render_template('question_detail.html', question=question)

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
                "subtopic": request.form['subtopic'],
                "source": request.form.get('source', '')
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
