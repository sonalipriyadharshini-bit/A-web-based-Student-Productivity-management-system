from flask import Flask, render_template, redirect, url_for, session, request, jsonify
import sqlite3
import os
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_PATH = "studyflow.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS pomodoro_sessions (
        id            INTEGER PRIMARY KEY,
        user_id       TEXT,
        subject       TEXT,
        duration_mins INTEGER,
        pause_count   INTEGER,
        focus_score   INTEGER,
        session_date  TEXT,
        created_at    TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id          INTEGER PRIMARY KEY,
        user_id     TEXT,
        title       TEXT,
        due_date    TEXT,
        priority    TEXT,
        status      TEXT,
        done        INTEGER,
        task_date   TEXT,
        created_at  TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS habits (
        id           INTEGER PRIMARY KEY,
        user_id      TEXT,
        name         TEXT,
        color        TEXT,
        streak       INTEGER,
        last_checked TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS habit_logs (
        id       INTEGER PRIMARY KEY,
        habit_id INTEGER,
        log_date TEXT,
        UNIQUE(habit_id, log_date)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        user_id     TEXT PRIMARY KEY,
        full_name   TEXT,
        email       TEXT,
        photo_url   TEXT,
        education   TEXT,
        major       TEXT,
        semester    TEXT,
        institution TEXT,
        target_gpa  TEXT,
        timezone    TEXT,
        wake_time   TEXT,
        sleep_time  TEXT,
        work_hours  TEXT,
        updated_at  TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def uid():
    return session.get('user_id')

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/pomodoro")
def pomodoro():
    return render_template("Pomodoro.html")

@app.route("/todo")
def todo():
    return render_template("todo.html")

@app.route("/timetable")
def timetable():
    return render_template("timetable.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/habits")
def habits():
    return render_template("habits.html")

@app.route("/api/set_user", methods=["POST"])
def set_user():
    data = request.get_json()
    session['user_id']    = data.get('uid')
    session['user_name']  = data.get('name', '')
    session['user_email'] = data.get('email', '')
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO profiles (user_id, full_name, email) VALUES (?, ?, ?)",
        (data.get('uid'), data.get('name', ''), data.get('email', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/api/dashboard_stats")
def dashboard_stats():
    user_id = uid()
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    today = str(date.today())
    conn  = get_db()
    c     = conn.cursor()
    c.execute("SELECT COALESCE(SUM(duration_mins),0) FROM pomodoro_sessions WHERE user_id=? AND session_date=?", (user_id, today))
    focus_mins = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM pomodoro_sessions WHERE user_id=? AND session_date=?", (user_id, today))
    sessions = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND task_date=?", (user_id, today))
    tasks_total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND task_date=? AND done=1", (user_id, today))
    tasks_done = c.fetchone()[0]
    c.execute("SELECT COALESCE(MAX(streak),0) FROM habits WHERE user_id=?", (user_id,))
    streak = c.fetchone()[0]
    c.execute("SELECT full_name, photo_url FROM profiles WHERE user_id=?", (user_id,))
    profile_row = c.fetchone()
    full_name = profile_row['full_name'] if profile_row else ''
    photo_url = profile_row['photo_url'] if profile_row else ''
    conn.close()
    h = focus_mins // 60
    m = focus_mins % 60
    return jsonify({
        "focus_time":  f"{h}h {m}m",
        "focus_mins":  focus_mins,
        "tasks":       f"{tasks_done}/{tasks_total}",
        "tasks_done":  tasks_done,
        "tasks_total": tasks_total,
        "streak":      f"{streak} days",
        "sessions":    sessions,
        "full_name":   full_name,
        "photo_url":   photo_url
    })

@app.route("/api/pomodoro/save", methods=["POST"])
def save_pomodoro():
    user_id = uid()
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "INSERT INTO pomodoro_sessions (user_id, subject, duration_mins, pause_count, focus_score, session_date, created_at) VALUES (?,?,?,?,?,?,?)",
        (
            user_id,
            data.get("subject", ""),
            data.get("duration_mins", 25),
            data.get("pause_count", 0),
            data.get("focus_score", 100),
            str(date.today()),
            str(datetime.now())
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})

@app.route("/api/pomodoro/history")
def pomodoro_history():
    user_id = uid()
    if not user_id:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pomodoro_sessions WHERE user_id=? ORDER BY id DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    user_id = uid()
    if not user_id:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id=? ORDER BY id DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/tasks/add", methods=["POST"])
def add_task():
    user_id = uid()
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    data  = request.get_json()
    today = str(date.today())
    conn  = get_db()
    conn.execute(
        "INSERT INTO tasks (user_id, title, due_date, priority, status, done, task_date, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (
            user_id,
            data.get("title"),
            data.get("due_date", ""),
            data.get("priority", "Medium"),
            data.get("status", "Not Started"),
            1 if data.get("status") == "Completed" else 0,
            today,
            str(datetime.now())
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "added"})

@app.route("/api/tasks/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET title=?, due_date=?, priority=?, status=?, done=? WHERE id=?",
        (
            data.get("title"),
            data.get("due_date", ""),
            data.get("priority", "Medium"),
            data.get("status", "Not Started"),
            1 if data.get("status") == "Completed" else 0,
            task_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})

@app.route("/api/tasks/done/<int:task_id>", methods=["POST"])
def mark_task_done(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done=1, status='Completed' WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "done"})

@app.route("/api/tasks/delete/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route("/api/habits", methods=["GET"])
def get_habits():
    user_id = uid()
    if not user_id:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM habits WHERE user_id=? ORDER BY streak DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/habits/add", methods=["POST"])
def add_habit():
    user_id = uid()
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "INSERT INTO habits (user_id, name, color, streak, last_checked) VALUES (?,?,?,?,?)",
        (user_id, data.get("name"), data.get("color", "#f6a400"), 0, "")
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "added"})

@app.route("/api/habits/check/<int:habit_id>", methods=["POST"])
def check_habit(habit_id):
    today = str(date.today())
    conn  = get_db()
    try:
        conn.execute(
            "INSERT INTO habit_logs (habit_id, log_date) VALUES (?,?)",
            (habit_id, today)
        )
        conn.execute(
            "UPDATE habits SET streak=streak+1, last_checked=? WHERE id=?",
            (today, habit_id)
        )
        conn.commit()
        status = "checked"
    except sqlite3.IntegrityError:
        status = "already_checked"
    conn.close()
    return jsonify({"status": status})

@app.route("/api/habits/uncheck/<int:habit_id>", methods=["POST"])
def uncheck_habit(habit_id):
    today = str(date.today())
    conn  = get_db()
    conn.execute("DELETE FROM habit_logs WHERE habit_id=? AND log_date=?", (habit_id, today))
    conn.execute("UPDATE habits SET streak=MAX(0,streak-1) WHERE id=? AND last_checked=?", (habit_id, today))
    conn.commit()
    conn.close()
    return jsonify({"status": "unchecked"})

@app.route("/api/habits/logs/<int:habit_id>")
def habit_logs(habit_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT log_date FROM habit_logs WHERE habit_id=? ORDER BY log_date DESC",
        (habit_id,)
    ).fetchall()
    conn.close()
    return jsonify([r['log_date'] for r in rows])

@app.route("/api/habits/all_logs")
def all_habit_logs():
    user_id = uid()
    if not user_id:
        return jsonify({})
    conn = get_db()
    rows = conn.execute(
        '''SELECT hl.habit_id, hl.log_date FROM habit_logs hl
           JOIN habits h ON h.id=hl.habit_id
           WHERE h.user_id=?''',
        (user_id,)
    ).fetchall()
    conn.close()
    logs = {}
    for r in rows:
        key = f"{r['habit_id']}_{r['log_date']}"
        logs[key] = True
    return jsonify(logs)

@app.route("/api/habits/delete/<int:habit_id>", methods=["DELETE"])
def delete_habit(habit_id):
    conn = get_db()
    conn.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    conn.execute("DELETE FROM habit_logs WHERE habit_id=?", (habit_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})

@app.route("/api/profile", methods=["GET"])
def get_profile():
    user_id = uid()
    if not user_id:
        return jsonify({}), 401
    conn = get_db()
    row  = conn.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return jsonify(dict(row) if row else {})

@app.route("/api/profile/save", methods=["POST"])
def save_profile():
    user_id = uid()
    if not user_id:
        return jsonify({"error": "not logged in"}), 401
    data = request.get_json()
    conn = get_db()
    conn.execute(
        '''INSERT INTO profiles
            (user_id, full_name, email, photo_url, education, major, semester,
             institution, target_gpa, timezone, wake_time, sleep_time, work_hours, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(user_id) DO UPDATE SET
               full_name   = excluded.full_name,
               email       = excluded.email,
               photo_url   = excluded.photo_url,
               education   = excluded.education,
               major       = excluded.major,
               semester    = excluded.semester,
               institution = excluded.institution,
               target_gpa  = excluded.target_gpa,
               timezone    = excluded.timezone,
               wake_time   = excluded.wake_time,
               sleep_time  = excluded.sleep_time,
               work_hours  = excluded.work_hours,
               updated_at  = excluded.updated_at
        ''',
        (
            user_id,
            data.get("full_name", ""),
            data.get("email", ""),
            data.get("photo_url", ""),
            data.get("education", ""),
            data.get("major", ""),
            data.get("semester", ""),
            data.get("institution", ""),
            data.get("target_gpa", ""),
            data.get("timezone", ""),
            data.get("wake_time", ""),
            data.get("sleep_time", ""),
            data.get("work_hours", ""),
            str(datetime.now())
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "saved"})

if __name__ == "__main__":
    app.run(debug=True)
