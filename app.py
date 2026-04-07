from flask import session
import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_from_directory
from PIL import Image
#import pytesseract

 #pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🟢 Create app FIRST
app = Flask(__name__)
app.secret_key = "secret123"
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")

# 🟢 Upload folder config
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 🟢 Parking capacity
TOTAL_SLOTS = 5

# 🟢 Create DB
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT,
        entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        exit_time TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# 🏠 Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        plate = request.form.get("plate")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO vehicles (plate) VALUES (?)", (plate,))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("index.html")

# 📊 Dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vehicles WHERE exit_time IS NULL")
    active = cursor.fetchall()

    cursor.execute("SELECT * FROM vehicles")
    all_data = cursor.fetchall()

    conn.close()

    available_slots = TOTAL_SLOTS - len(active)

    return render_template(
        "dashboard.html",
        active=active,
        all_data=all_data,
        available=available_slots
    )

# 🚪 Exit Vehicle
@app.route("/exit/<int:id>")
def exit_vehicle(id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE vehicles SET exit_time=CURRENT_TIMESTAMP WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# 📸 Upload Page
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        file = request.files["image"]

        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # OCR
            text = "TEST123"   # temporary for deployment

            # Save to DB
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO vehicles (plate) VALUES (?)", (text,))
            conn.commit()
            conn.close()

            return render_template("upload.html", image=file.filename, plate=text)

    return render_template("upload.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# 🖼 Serve uploaded images (IMPORTANT)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ▶ Run app
if __name__ == "__main__":
    app.run(debug=True)
