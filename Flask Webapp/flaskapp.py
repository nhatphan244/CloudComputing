from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # For session management

DATABASE = 'users.db'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn

# Ensure the database and table exist
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                address TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()  # Initialize the database at startup

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = hashlib.sha256(request.form['password'].encode()).hexdigest()  # Hash password
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    email = request.form['email']
    address = request.form['address']

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, first_name, last_name, email, address) VALUES (?, ?, ?, ?, ?, ?)",
                      (username, password, first_name, last_name, email, address))
            conn.commit()
            session['username'] = username  # Store username in session
        return redirect(url_for('profile', username=username))
    except sqlite3.IntegrityError:
        return "Username or Email already exists. Please choose another."

@app.route('/profile/<username>')
def profile(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

    if user:
        return render_template('profile.html', user=user)
    return "User not found", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()  # Hash password

        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()

        if user:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        return "Invalid username or password"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
