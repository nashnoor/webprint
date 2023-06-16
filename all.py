import sqlite3
import os
import sys
from flask import Flask, request, render_template, redirect, url_for, current_app
import cups
import tempfile
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

#login system

app = Flask(__name__)
app.secret_key = '<your-secret-key>' #you may use 'openssl rand -base64 12'

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id
        self.username = None
        self.password = None
        self.load_user_data()

    def load_user_data(self):
        with current_app.app_context():
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM users WHERE id=?", (self.id,))
            result = cursor.fetchone()
            if result:
                self.username = result[0]
                self.password = result[1]


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def get_db():
    ctx = current_app.app_context()
    if not hasattr(ctx, 'sqlite_db'):
        ctx.sqlite_db = sqlite3.connect('users.db')
    return ctx.sqlite_db


@app.teardown_appcontext
def close_db(exception=None):
    ctx = current_app.app_context()
    if hasattr(ctx, 'sqlite_db'):
        ctx.sqlite_db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result and result[1] == password:
            user = User(result[0])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
#webprint

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        conn = cups.Connection()
        upload = request.files['upload']
        with tempfile.NamedTemporaryFile() as fp:
            upload.save(fp.name)
            conn.printFile(app.config['printer_name'], fp.name, 'WebPrinter', {})
        return render_template('success.html')
    
if __name__ == '__main__':
    args = sys.argv
    port = int(args[1])
    printer_name = args[2]
    app.config['printer_name'] = printer_name
    app.run(host='0.0.0.0', port=port)

