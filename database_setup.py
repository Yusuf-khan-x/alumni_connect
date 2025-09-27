import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Alumni Table
c.execute('''
CREATE TABLE IF NOT EXISTS alumni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    graduation_year TEXT,
    career TEXT
)
''')

# Users Table (for login)
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Events Table
c.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
''')

# Mentorship Table
c.execute('''
CREATE TABLE IF NOT EXISTS mentorship (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_name TEXT NOT NULL,
    expertise TEXT NOT NULL,
    details TEXT
)
''')

# Mentorship Requests Table (for students)
c.execute('''
CREATE TABLE IF NOT EXISTS mentorship_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    email TEXT,
    field_of_interest TEXT NOT NULL
)
''')

conn.commit()
conn.close()