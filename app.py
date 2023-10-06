import os
import cv2
import sqlite3
import pickle
import numpy as np
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, render_template, request, redirect, url_for, session,  jsonify
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


app.secret_key = 'my_key_to_WRP'


app.config['UPLOAD_FOLDER'] = './static/uploads'  # Folder to store uploaded images
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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



@app.route('/upload', methods=['POST'])
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

        return home()

    return 'Invalid file or file extension.'




# Load the pickled model
with open('https://drive.google.com/file/d/1IodlUzT1DmY-Dv4c6bV4kD2T73sEE-ci/view?usp=drive_link', 'rb') as model_file:
    model = pickle.load(model_file)


def preprocess_image(img):
    img = cv2.resize(img, (224, 224))  # Resize the image to match the model's input shape
    img = img.astype(np.float32) / 255.0  # Normalize the image
    return img

def predict_class(img):
    img = preprocess_image(img)
    img = np.expand_dims(img, axis=0)
    return model.predict(img)



@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), -1)
        prediction = predict_class(img)
        predicted_class = np.argmax(prediction)
        return render_template('index.html', predicted_class=predicted_class)
    
    return redirect(url_for('home'))



# Create SQLite database and table
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE,
              password TEXT)''')
conn.commit()
conn.close()




# Function to hash the password
def hash_password(password):
    return generate_password_hash(password)

# Function to verify hashed password
def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = hash_password(password)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        return render_template('login.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and verify_password(user[2], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials. Please try again.'

    return render_template('login.html')



@app.route('/')
def home():
    username = session.get('username')
    if username:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT filename FROM images ORDER BY id DESC LIMIT 5')
        images = c.fetchall()
        conn.close()

        return render_template('index.html', images=images)
        
        # return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))



@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/predict')
def rpedicted():
    return render_template('predict.html')





if __name__ == '__main__':
    app.run(debug=True)
