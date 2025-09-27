from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Alumni table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS alumni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        graduation_year INTEGER,
        career TEXT,
        skills TEXT
    )
    ''')

    # Student table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        year INTEGER,
        skills TEXT
    )
    ''')

    # Users table (for alumni logins)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Events table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        date TEXT
    )
    ''')

    # RSVP table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS rsvps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        student_email TEXT
    )
    ''')

    conn.commit()
    conn.close()

with app.app_context():
    init_db()

@app.route('/')
def index():
    user = session.get('user')
    student = session.get('student')
    return render_template('index.html', user=user, student=student)

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        graduation_year = request.form['graduation_year']
        career = request.form['career']
        skills = request.form['skills']
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO alumni (name, email, password, graduation_year, career, skills) VALUES (?, ?, ?, ?, ?, ?)',
                         (name, email, hashed_pw, graduation_year, career, skills))
            conn.commit()
            flash('Alumni registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()
    return render_template('register_user.html')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        year = request.form['year']
        skills = request.form['skills']
        hashed_pw = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO students (name, email, password, year, skills) VALUES (?, ?, ?, ?, ?)',
                         (name, email, hashed_pw, year, skills))
            conn.commit()
            flash('Student registration successful. Please log in.', 'success')
            return redirect(url_for('login_student'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()
    return render_template('register_student.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        alumni = conn.execute('SELECT * FROM alumni WHERE email=?', (email,)).fetchone()
        conn.close()
        if alumni and check_password_hash(alumni['password'], password):
            session['user'] = email
            flash('Logged in as alumni!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        student = conn.execute('SELECT * FROM students WHERE email=?', (email,)).fetchone()
        conn.close()
        if student and check_password_hash(student['password'], password):
            session['student'] = email
            flash('Logged in as student!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login_student.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('student', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/events', methods=['GET', 'POST'])
def events():
    user = session.get('user')
    student = session.get('student')
    conn = get_db_connection()
    if request.method == 'POST':
        if user:
            # Alumni can post events
            title = request.form.get('title')
            description = request.form.get('description')
            date = request.form.get('date')
            if title and date:
                conn.execute('INSERT INTO events (title, description, date) VALUES (?, ?, ?)',
                             (title, description, date))
                conn.commit()
                flash("Event posted successfully!", "success")
            else:
                flash("Title and date are required.", "danger")
        elif student and request.form.get('rsvp_event_id'):
            # Student RSVP
            event_id = request.form.get('rsvp_event_id')
            student_email = student
            conn.execute('INSERT INTO rsvps (event_id, student_email) VALUES (?, ?)', (event_id, student_email))
            conn.commit()
            flash("RSVP submitted!", "success")
        else:
            flash("You must be logged in to post or RSVP.", "danger")
    events = conn.execute('SELECT * FROM events ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('events.html', events=events, user=user, student=student)

@app.route('/match')
def match():
    user = session.get('user')
    student = session.get('student')
    conn = get_db_connection()
    if user:
        students = conn.execute('SELECT * FROM students').fetchall()
        conn.close()
        return render_template('match.html', students=students, user=user)
    elif student:
        alumni = conn.execute('SELECT * FROM alumni').fetchall()
        conn.close()
        return render_template('match.html', alumni=alumni, student=student)
    else:
        conn.close()
        flash('Please login first!', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)