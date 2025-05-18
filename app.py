import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import pickle
import sqlite3
import warnings
from werkzeug.security import generate_password_hash, check_password_hash

warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Database Setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     username TEXT UNIQUE, email TEXT UNIQUE, password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Load Model
filename = 'model/model.pkl'
model = pickle.load(open(filename, 'rb'))
filename1 = 'model2.pkl'
model2 = pickle.load(open(filename1, 'rb'))



@app.route('/home')
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username or email already exists')
    
    return render_template('register.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    int_features = [int(x) for x in request.form.values()]
    final_features = np.array([int_features])  
    prediction = model.predict(final_features)
    output = round(float(prediction[0]), 2)  

    if output == 0:
        result_text = 'LOAN APPROVAL ❌'
    else:
        result_text = 'LOAN APPROVAL ✅'
    
    return render_template('result.html', prediction_text=result_text)

@app.route('/predict1',methods=['POST'])
def predict1():

    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model2.predict(final_features)

    output = round(prediction[0], 2)
    if  output==0:              
        
        result_t='LOAN APPROVAL ❌'
    else:        
        result_t='LOAN APPROVAL ✅'

    return render_template('result1.html', prediction_t=result_t)


@app.route('/results',methods=['POST'])
def results1():

    data = request.get_json(force=True)
    prediction = model2.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

@app.route('/education')
def education():
    return render_template('education.html')


if __name__ == "__main__":
    app.run(debug=False, port=800)
