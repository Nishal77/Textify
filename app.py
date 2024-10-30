from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import os
from ocr_pro import ocr_core
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import openpyxl
import bcrypt
from auth import register_user, generate_password, authenticate_user, get_user_id_from_database

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff', 'tif', 'pdf'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database setup
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')
conn.commit()
conn.close()

@app.route('/extract_text', methods=['POST'])
async def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        extracted_text = await ocr_core(file_path)
        return jsonify({'extracted_text': extracted_text})
    else:
        return jsonify({'error': 'Unsupported file type'}), 400

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username:
            error_message = "Please enter a username."
            return render_template("login.html", error=error_message)

        if not password:
            error_message = "Please enter a password."
            return render_template("login.html", error=error_message)

        if authenticate_user(username, password):
            session['username'] = username
            success_message = "Login successful!"
            return render_template("upload.html", success=success_message, login_success=1)
        # In your login route
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template("login.html", error=error_message)
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['usrnm']
        email = request.form['email']
        password = request.form['password']

        # Register the user
        registered_username, error_message = register_user(username, email, password)
        if registered_username is None:
            return render_template("signup.html", error=error_message)

        return render_template("signup.html", success=f"Registration successful! Your username is {registered_username}. Go to the login page to log in.")
    return render_template("signup.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/upload", methods=['GET', 'POST'])
async def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving file to: {file_path}")
            file.save(file_path)
            extracted_text = await ocr_core(file_path)
            _, extension = os.path.splitext(filename)
            if extension.lower() == '.pdf':
                pdf_url = url_for('static', filename='uploads/' + filename)
                return render_template('upload.html', success_msg='Image/PDF successfully uploaded and processed', extracted_text=extracted_text, pdf_url=pdf_url)
            else:
                img_src = url_for('static', filename='uploads/' + filename)
                return render_template('upload.html', success_msg='Image/PDF successfully uploaded and processed', extracted_text=extracted_text, img_src=img_src)
        else:
            return render_template('upload.html', msg='No file selected or unsupported file type')
    return render_template('upload.html')

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)