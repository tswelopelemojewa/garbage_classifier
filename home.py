from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT
    )
''')

conn.commit()
conn.close()


# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Save file path to the database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO images (filename) VALUES (?)', (filename,))
        conn.commit()
        conn.close()

        return display_images()

    return 'Invalid file or file extension.'


@app.route('/')
def display_images():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT filename FROM images ORDER BY id DESC')
    images = c.fetchall()
    conn.close()

    return render_template('index.html', images=images)
