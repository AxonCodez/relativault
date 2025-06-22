from flask import Flask, render_template, request, session, redirect, url_for, flash
import json
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load questions from JSON
with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r') as f:
    questions = json.load(f)

# Load users from JSON (create if not exists)
USER_FILE = os.path.join(os.path.dirname(__file__), 'users.json')
if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump([], f)
with open(USER_FILE, 'r') as f:
    users = json.load(f)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if any(u['username'] == username for u in users):
            flash('Username already exists')
        else:
            users.append({'username': username, 'password': password})
            with open(USER_FILE, 'w') as f:
                json.dump(users, f, indent=2)
            session['user'] = username
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/subtopics')
def subtopics():
    if 'user' not in session:
        return redirect(url_for('login'))
    counts = get_subtopic_counts()
    return render_template('subtopics.html', subtopics=SUBTOPICS, counts=counts)

@app.route('/questions/<subtopic>')
def show_questions_by_subtopic(subtopic):
    if 'user' not in session:
        return redirect(url_for('login'))
    normalized = subtopic.replace('-', ' ').lower()
    filtered = [q for q in questions if q.get("subtopic", "").lower().replace('-', ' ') == normalized]
    return render_template('questions_list.html', questions=filtered, subtopic=subtopic.title())

@app.route('/question/<int:qid>')
def question_detail(qid):
    if 'user' not in session:
        return redirect(url_for('login'))
    question = next((q for q in questions if q["id"] == qid), None)
    if not question:
        return "Question not found", 404
    # Find next question in the same subtopic
    subtopic_questions = [q for q in questions if q["subtopic"] == question["subtopic"]]
    current_index = next(i for i, q in enumerate(subtopic_questions) if q["id"] == qid)
    next_id = subtopic_questions[current_index + 1]["id"] if current_index + 1 < len(subtopic_questions) else None
    return render_template('question_detail.html', question=question, next_id=next_id)

if __name__ == '__main__':
    app.run(debug=True)
