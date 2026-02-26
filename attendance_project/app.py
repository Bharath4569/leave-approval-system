from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "leave_secret"

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    password TEXT,
                    role TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    from_date TEXT,
                    to_date TEXT,
                    reason TEXT,
                    status TEXT,
                    month TEXT
                )''')

    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=? AND role=?",
                  (email, password, role))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["role"] = role

            if role == "employee":
                return redirect("/employee")
            else:
                return redirect("/manager")
        else:
            return "Invalid Login"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  (name, email, password, role))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/employee", methods=["GET", "POST"])
def employee():
    if session.get("role") != "employee":
        return redirect("/")

    user_id = session["user_id"]

    if request.method == "POST":
        from_date = request.form["from"]
        to_date = request.form["to"]
        reason = request.form["reason"]
        month = datetime.strptime(from_date, "%Y-%m-%d").strftime("%B")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""INSERT INTO leaves 
                     (user_id,from_date,to_date,reason,status,month)
                     VALUES (?,?,?,?,?,?)""",
                  (user_id, from_date, to_date, reason, "Pending", month))
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leaves WHERE user_id=?", (user_id,))
    leaves = c.fetchall()
    conn.close()

    return render_template("employee_dashboard.html", leaves=leaves)


@app.route("/manager")
def manager():
    if session.get("role") != "manager":
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    
    c.execute("""SELECT leaves.id, users.name, users.email,
                 leaves.from_date, leaves.to_date,
                 leaves.reason, leaves.status, leaves.month
                 FROM leaves
                 JOIN users ON leaves.user_id = users.id""")
    leaves = c.fetchall()

    
    c.execute("SELECT id, name, email, role FROM users")
    users = c.fetchall()

    conn.close()

    return render_template("manager_dashboard.html",
                           leaves=leaves,
                           users=users)

@app.route("/update/<int:id>/<status>")
def update(id, status):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE leaves SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()
    return redirect("/manager")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)