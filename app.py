from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="messagedb",
            user="postgres",
            password="Maxelo@2023",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Create messages table if it doesn't exist
def init_db():
    conn = get_db_connection()
    if conn is None:
        print("Could not initialize database: connection failed")
        return
        
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone_number VARCHAR(15) NOT NULL,
                message TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        try:
            # Get form data
            name = request.form["name"]
            email = request.form["email"]
            phone_number = request.form["phone_number"]
            message_text = request.form["message"]
            
            # Validate required fields
            if not all([name, email, phone_number, message_text]):
                flash("Please fill in all required fields", "error")
                return redirect(url_for("index"))
            
            # Insert into database
            conn = get_db_connection()
            if conn is None:
                flash("Database connection error. Please try again later.", "error")
                return redirect(url_for("index"))
                
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO messages (name, email, phone_number, message) VALUES (%s, %s, %s, %s)",
                (name, email, phone_number, message_text)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
            print("Error:", e)
            flash("An error occurred while submitting your message. Please try again.", "error")
            return redirect(url_for("index"))

@app.route("/messages")
def view_messages():
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error. Please try again later.", "error")
            return redirect(url_for("index"))
            
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages ORDER BY id")
        all_messages = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template("view_request.html", messages=all_messages)
    except Exception as e:
        print("Error:", e)
        flash("An error occurred while retrieving messages.", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)