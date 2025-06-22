from flask import Flask, render_template, request, session, redirect, url_for, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )

@app.route('/')
def index():
    session['streak'] = session.get('streak', 0)
    return render_template('index.html', streak=session['streak'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s;', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
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
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s);', (username, password))
            conn.commit()
            session['user'] = username
            return redirect(url_for('index'))
        except psycopg2.IntegrityError:
            flash('Username already exists')
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/subtopics')
def subtopics():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT subtopic FROM questions;')
    subtopics = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('subtopics.html', subtopics=subtopics)

@app.route('/questions/<subtopic>')
def show_questions_by_subtopic(subtopic):
    if 'user' not in session:
        return redirect(url_for('login'))
    normalized = subtopic.replace('-', ' ').lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM questions WHERE subtopic = %s;', (normalized,))
    questions = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('questions_list.html', questions=[
        {
            'id': q[0],
            'text': q[1],
            'options': q[2],
            'answer': q[3],
            'subtopic': q[4],
            'source': q[5]
        } for q in questions
    ], subtopic=subtopic.title())

@app.route('/question/<int:qid>')
def question_detail(qid):
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM questions WHERE id = %s;', (qid,))
    question = cur.fetchone()
    # Find next question in the same subtopic
    cur.execute('SELECT id FROM questions WHERE subtopic = (SELECT subtopic FROM questions WHERE id = %s) ORDER BY id;', (qid,))
    subtopic_questions = [row[0] for row in cur.fetchall()]
    current_index = subtopic_questions.index(qid)
    next_id = subtopic_questions[current_index + 1] if current_index + 1 < len(subtopic_questions) else None
    cur.close()
    conn.close()
    if not question:
        return "Question not found", 404
    return render_template('question_detail.html', question={
        'id': question[0],
        'text': question[1],
        'options': question[2],
        'answer': question[3],
        'subtopic': question[4],
        'source': question[5]
    }, next_id=next_id)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Admin-only access (replace 'admin' with your admin username if needed)
    if session.get('user') != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        text = request.form['text']
        options = request.form.getlist('options[]')
        answer = int(request.form['answer'])
        subtopic = request.form['subtopic']
        source = request.form['source'] or None

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO questions (text, options, answer, subtopic, source) VALUES (%s, %s, %s, %s, %s);',
                (text, options, answer, subtopic, source)
            )
            conn.commit()
            flash('Question added successfully!', 'success')
        except Exception as e:
            flash('Error adding question: ' + str(e), 'error')
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('add_question'))
    return render_template('add_question.html')

if __name__ == '__main__':
    app.run(debug=True)
