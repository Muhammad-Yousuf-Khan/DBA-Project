# app.py  ─  Flask School Management System
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g, abort
)
import psycopg2
from datetime import date
from functools import wraps
from config import Config, DB_USERS, ROLE_PERMISSIONS
from db import get_connection, query, execute, query_one

app = Flask(__name__)
app.config.from_object(Config)

# ─────────────────────────────────────────────────────────────
# CONNECTION HELPER
# ─────────────────────────────────────────────────────────────
def get_db():
    if "db_conn" not in g:
        user = session.get("username")
        pwd  = session.get("db_password")
        if not user or not pwd:
            return None
        try:
            g.db_conn = get_connection(user, pwd)
        except Exception:
            return None
    return g.db_conn

@app.teardown_appcontext
def close_db(error):
    conn = g.pop("db_conn", None)
    if conn:
        conn.close()

# ─────────────────────────────────────────────────────────────
# AUTH DECORATORS
# ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def permission_required(perm):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            role  = session.get("role", "viewer")
            perms = ROLE_PERMISSIONS.get(role, [])
            if perm not in perms:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─────────────────────────────────────────────────────────────
# CONTEXT PROCESSOR
# ─────────────────────────────────────────────────────────────
@app.context_processor
def inject_user():
    return {
        "current_user": session.get("username"),
        "current_role": session.get("role"),
        "permissions":  ROLE_PERMISSIONS.get(session.get("role", ""), []),
    }

# ─────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404

# ═════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═════════════════════════════════════════════════════════════
@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user_cfg = DB_USERS.get(username)
        if not user_cfg or user_cfg["password"] != password:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        try:
            conn = get_connection(username, password)
            conn.close()
        except Exception as ex:
            flash(f"Database connection failed: {ex}", "danger")
            return render_template("login.html")

        session["username"]    = username
        session["db_password"] = password
        session["role"]        = user_cfg["role"]
        flash(f"Welcome, {username}! Logged in as {user_cfg['role']}.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# ═════════════════════════════════════════════════════════════
# DASHBOARD
# ═════════════════════════════════════════════════════════════
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    stats = {
        "students":      query_one(conn, "SELECT COUNT(*) AS c FROM students")["c"],
        "teachers":      query_one(conn, "SELECT COUNT(*) AS c FROM teachers")["c"],
        "classes":       query_one(conn, "SELECT COUNT(*) AS c FROM classes")["c"],
        "subjects":      query_one(conn, "SELECT COUNT(*) AS c FROM subjects")["c"],
        "unpaid_fees":   query_one(conn, "SELECT COUNT(*) AS c FROM fees WHERE status='unpaid'")["c"],
        "paid_fees":     query_one(conn, "SELECT COUNT(*) AS c FROM fees WHERE status='paid'")["c"],
        "total_fee_amt": query_one(conn, "SELECT COALESCE(SUM(amount),0) AS c FROM fees")["c"],
    }
    recent_students = query(conn, """
        SELECT s.student_id, s.first_name, s.last_name,
               c.class_name, s.admission_date, s.status
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
        ORDER BY s.student_id DESC LIMIT 8
    """)
    class_overview = query(conn, "SELECT * FROM class_overview ORDER BY class_id")
    return render_template("dashboard.html",
                           stats=stats,
                           recent_students=recent_students,
                           class_overview=class_overview)

# ═════════════════════════════════════════════════════════════
# STUDENTS
# ═════════════════════════════════════════════════════════════
@app.route("/students")
@login_required
def students_list():
    conn   = get_db()
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    params = []
    where  = []

    if search:
        where.append("(s.first_name ILIKE %s OR s.last_name ILIKE %s)")
        params += [f"%{search}%", f"%{search}%"]
    if status:
        where.append("s.status = %s")
        params.append(status)

    sql = """
        SELECT s.student_id, s.first_name, s.last_name, s.gender,
               s.date_of_birth, c.class_name, s.admission_date, s.status
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY s.student_id DESC"

    students = query(conn, sql, params)
    return render_template("students/list.html",
                           students=students, search=search, status=status)

@app.route("/students/add", methods=["GET", "POST"])
@login_required
@permission_required("write")
def students_add():
    conn    = get_db()
    classes = query(conn, "SELECT class_id, class_name FROM classes ORDER BY class_id")

    if request.method == "POST":
        try:
            execute(conn, """
                INSERT INTO students
                (first_name, last_name, date_of_birth, gender,
                 class_id, admission_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form["first_name"],
                request.form.get("last_name")      or None,
                request.form.get("date_of_birth")  or None,
                request.form.get("gender"),
                request.form.get("class_id")       or None,
                request.form.get("admission_date") or None,
                request.form.get("status", "active"),
            ))
            flash("Student added successfully!", "success")
            return redirect(url_for("students_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("students/add.html", classes=classes)

@app.route("/students/edit/<int:sid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def students_edit(sid):
    conn    = get_db()
    student = query_one(conn, "SELECT * FROM students WHERE student_id=%s", (sid,))
    classes = query(conn, "SELECT class_id, class_name FROM classes ORDER BY class_id")

    if not student:
        abort(404)

    if request.method == "POST":
        try:
            execute(conn, """
                UPDATE students
                SET first_name=%s, last_name=%s, date_of_birth=%s,
                    gender=%s, class_id=%s, admission_date=%s, status=%s
                WHERE student_id=%s
            """, (
                request.form["first_name"],
                request.form.get("last_name")      or None,
                request.form.get("date_of_birth")  or None,
                request.form.get("gender"),
                request.form.get("class_id")       or None,
                request.form.get("admission_date") or None,
                request.form.get("status", "active"),
                sid,
            ))
            flash("Student updated successfully!", "success")
            return redirect(url_for("students_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("students/edit.html", student=student, classes=classes)

@app.route("/students/delete/<int:sid>", methods=["POST"])
@login_required
@permission_required("delete")
def students_delete(sid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM students WHERE student_id=%s", (sid,))
        flash("Student deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("students_list"))

# ═════════════════════════════════════════════════════════════
# TEACHERS
# ═════════════════════════════════════════════════════════════
@app.route("/teachers")
@login_required
def teachers_list():
    conn     = get_db()
    search   = request.args.get("search", "").strip()
    teachers = query(conn, """
        SELECT teacher_id, name, email, phone, hire_date
        FROM teachers
        WHERE name ILIKE %s OR email ILIKE %s
        ORDER BY teacher_id DESC
    """, (f"%{search}%", f"%{search}%"))
    return render_template("teachers/list.html", teachers=teachers, search=search)

@app.route("/teachers/add", methods=["GET", "POST"])
@login_required
@permission_required("write")
def teachers_add():
    conn = get_db()
    if request.method == "POST":
        try:
            execute(conn, """
                INSERT INTO teachers (name, email, phone, hire_date)
                VALUES (%s, %s, %s, %s)
            """, (
                request.form["name"],
                request.form.get("email")     or None,
                request.form.get("phone")     or None,
                request.form.get("hire_date") or None,
            ))
            flash("Teacher added successfully!", "success")
            return redirect(url_for("teachers_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("teachers/add.html")

@app.route("/teachers/edit/<int:tid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def teachers_edit(tid):
    conn    = get_db()
    teacher = query_one(conn, "SELECT * FROM teachers WHERE teacher_id=%s", (tid,))
    if not teacher:
        abort(404)

    if request.method == "POST":
        try:
            execute(conn, """
                UPDATE teachers
                SET name=%s, email=%s, phone=%s, hire_date=%s
                WHERE teacher_id=%s
            """, (
                request.form["name"],
                request.form.get("email")     or None,
                request.form.get("phone")     or None,
                request.form.get("hire_date") or None,
                tid,
            ))
            flash("Teacher updated! (audit log recorded)", "success")
            return redirect(url_for("teachers_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("teachers/edit.html", teacher=teacher)

@app.route("/teachers/delete/<int:tid>", methods=["POST"])
@login_required
@permission_required("delete")
def teachers_delete(tid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM teachers WHERE teacher_id=%s", (tid,))
        flash("Teacher deleted! (audit log recorded)", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("teachers_list"))

# ═════════════════════════════════════════════════════════════
# CLASSES
# ═════════════════════════════════════════════════════════════
@app.route("/classes")
@login_required
def classes_list():
    conn    = get_db()
    classes = query(conn, """
        SELECT c.class_id, c.class_name, t.name AS incharge,
               COUNT(s.student_id) AS total_students
        FROM classes c
        LEFT JOIN teachers t ON c.class_incharge = t.teacher_id
        LEFT JOIN students s ON c.class_id = s.class_id
        GROUP BY c.class_id, c.class_name, t.name
        ORDER BY c.class_id
    """)
    return render_template("classes/list.html", classes=classes)

@app.route("/classes/add", methods=["GET", "POST"])
@login_required
@permission_required("write")
def classes_add():
    conn     = get_db()
    teachers = query(conn, "SELECT teacher_id, name FROM teachers ORDER BY name")
    if request.method == "POST":
        try:
            execute(conn, """
                INSERT INTO classes (class_name, class_incharge) VALUES (%s, %s)
            """, (
                request.form["class_name"],
                request.form.get("class_incharge") or None,
            ))
            flash("Class added!", "success")
            return redirect(url_for("classes_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("classes/add.html", teachers=teachers)

@app.route("/classes/edit/<int:cid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def classes_edit(cid):
    conn     = get_db()
    cls      = query_one(conn, "SELECT * FROM classes WHERE class_id=%s", (cid,))
    teachers = query(conn, "SELECT teacher_id, name FROM teachers ORDER BY name")
    if not cls:
        abort(404)

    if request.method == "POST":
        try:
            execute(conn, """
                UPDATE classes SET class_name=%s, class_incharge=%s WHERE class_id=%s
            """, (
                request.form["class_name"],
                request.form.get("class_incharge") or None,
                cid,
            ))
            flash("Class updated!", "success")
            return redirect(url_for("classes_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("classes/edit.html", cls=cls, teachers=teachers)

@app.route("/classes/delete/<int:cid>", methods=["POST"])
@login_required
@permission_required("delete")
def classes_delete(cid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM classes WHERE class_id=%s", (cid,))
        flash("Class deleted!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("classes_list"))

# ═════════════════════════════════════════════════════════════
# SUBJECTS
# ═════════════════════════════════════════════════════════════
@app.route("/subjects")
@login_required
def subjects_list():
    conn     = get_db()
    subjects = query(conn, "SELECT * FROM subjects ORDER BY subject_id")
    return render_template("subjects/list.html", subjects=subjects)

@app.route("/subjects/add", methods=["GET", "POST"])
@login_required
@permission_required("write")
def subjects_add():
    conn = get_db()
    if request.method == "POST":
        try:
            execute(conn, "INSERT INTO subjects (subject_name) VALUES (%s)",
                    (request.form["subject_name"],))
            flash("Subject added!", "success")
            return redirect(url_for("subjects_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("subjects/add.html")

@app.route("/subjects/edit/<int:sid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def subjects_edit(sid):
    conn    = get_db()
    subject = query_one(conn, "SELECT * FROM subjects WHERE subject_id=%s", (sid,))
    if not subject:
        abort(404)
    if request.method == "POST":
        try:
            execute(conn, "UPDATE subjects SET subject_name=%s WHERE subject_id=%s",
                    (request.form["subject_name"], sid))
            flash("Subject updated!", "success")
            return redirect(url_for("subjects_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("subjects/edit.html", subject=subject)

@app.route("/subjects/delete/<int:sid>", methods=["POST"])
@login_required
@permission_required("delete")
def subjects_delete(sid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM subjects WHERE subject_id=%s", (sid,))
        flash("Subject deleted!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("subjects_list"))

# ═════════════════════════════════════════════════════════════
# ASSIGNMENTS
# ═════════════════════════════════════════════════════════════
@app.route("/assignments")
@login_required
def assignments_list():
    conn        = get_db()
    assignments = query(conn, """
        SELECT tcs.id, t.name AS teacher, c.class_name, s.subject_name
        FROM teacher_class_subject tcs
        JOIN teachers t ON tcs.teacher_id = t.teacher_id
        JOIN classes  c ON tcs.class_id   = c.class_id
        JOIN subjects s ON tcs.subject_id = s.subject_id
        ORDER BY c.class_name, s.subject_name
    """)
    teachers = query(conn, "SELECT teacher_id, name FROM teachers ORDER BY name")
    classes  = query(conn, "SELECT class_id, class_name FROM classes ORDER BY class_name")
    subjects = query(conn, "SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")
    return render_template("assignments/list.html",
                           assignments=assignments,
                           teachers=teachers,
                           classes=classes,
                           subjects=subjects)

@app.route("/assignments/add", methods=["POST"])
@login_required
@permission_required("write")
def assignments_add():
    conn = get_db()
    try:
        execute(conn, """
            INSERT INTO teacher_class_subject (teacher_id, class_id, subject_id)
            VALUES (%s, %s, %s)
        """, (
            request.form["teacher_id"],
            request.form["class_id"],
            request.form["subject_id"],
        ))
        flash("Assignment added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("assignments_list"))

@app.route("/assignments/delete/<int:aid>", methods=["POST"])
@login_required
@permission_required("delete")
def assignments_delete(aid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM teacher_class_subject WHERE id=%s", (aid,))
        flash("Assignment removed!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("assignments_list"))

# ═════════════════════════════════════════════════════════════
# FEES
# ═════════════════════════════════════════════════════════════
@app.route("/fees")
@login_required
def fees_list():
    conn   = get_db()
    status = request.args.get("status", "")
    search = request.args.get("search", "").strip()
    params = []
    where  = []

    if status:
        where.append("f.status = %s")
        params.append(status)
    if search:
        where.append("(s.first_name ILIKE %s OR s.last_name ILIKE %s)")
        params += [f"%{search}%", f"%{search}%"]

    sql = """
        SELECT f.fee_id, s.student_id, s.first_name, s.last_name,
               c.class_name, f.amount, f.due_date, f.paid_date, f.status
        FROM fees f
        JOIN students s ON f.student_id = s.student_id
        LEFT JOIN classes c ON s.class_id = c.class_id
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY f.fee_id DESC"

    fees     = query(conn, sql, params)
    students = query(conn, """
        SELECT student_id, first_name, last_name
        FROM students ORDER BY first_name
    """)
    return render_template("fees/list.html",
                           fees=fees, students=students,
                           status=status, search=search)

@app.route("/fees/add", methods=["POST"])
@login_required
@permission_required("write")
def fees_add():
    conn = get_db()
    try:
        execute(conn, """
            INSERT INTO fees (student_id, amount, due_date, status)
            VALUES (%s, %s, %s, 'unpaid')
        """, (
            request.form["student_id"],
            request.form["amount"],
            request.form.get("due_date") or None,
        ))
        flash("Fee record added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("fees_list"))

@app.route("/fees/edit/<int:fid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def fees_edit(fid):
    conn = get_db()
    fee  = query_one(conn, """
        SELECT f.fee_id, f.student_id, f.amount, f.due_date,
               f.paid_date, f.status,
               s.first_name, s.last_name, c.class_name
        FROM fees f
        JOIN students s ON f.student_id = s.student_id
        LEFT JOIN classes c ON s.class_id = c.class_id
        WHERE f.fee_id = %s
    """, (fid,))

    if not fee:
        abort(404)

    if request.method == "POST":
        try:
            paid_date = request.form.get("paid_date") or None
            status    = request.form.get("status", "unpaid")

            if status == "paid" and not paid_date:
                paid_date = date.today().isoformat()
            if status == "unpaid":
                paid_date = None

            execute(conn, """
                UPDATE fees
                SET amount=%s, due_date=%s, paid_date=%s, status=%s
                WHERE fee_id=%s
            """, (
                float(request.form["amount"]),
                request.form.get("due_date") or None,
                paid_date,
                status,
                fid,
            ))
            flash("Fee record updated successfully!", "success")
            return redirect(url_for("fees_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("fees/edit.html", fee=fee)

@app.route("/fees/pay/<int:fid>", methods=["POST"])
@login_required
@permission_required("update")
def fees_pay(fid):
    conn = get_db()
    try:
        execute(conn, """
            UPDATE fees SET status='paid', paid_date=CURRENT_DATE WHERE fee_id=%s
        """, (fid,))
        flash("Fee marked as paid!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("fees_list"))

@app.route("/fees/delete/<int:fid>", methods=["POST"])
@login_required
@permission_required("delete")
def fees_delete(fid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM fees WHERE fee_id=%s", (fid,))
        flash("Fee record deleted!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("fees_list"))

# ═════════════════════════════════════════════════════════════
# CONTACTS
# ═════════════════════════════════════════════════════════════
@app.route("/contacts")
@login_required
def contacts_list():
    conn     = get_db()
    search   = request.args.get("search", "").strip()
    contacts = query(conn, """
        SELECT ci.contact_id, s.student_id, s.first_name, s.last_name,
               ci.guardian_name, ci.relation, ci.phone, ci.address
        FROM contact_info ci
        JOIN students s ON ci.student_id = s.student_id
        WHERE ci.guardian_name ILIKE %s OR s.first_name ILIKE %s
        ORDER BY ci.contact_id DESC
    """, (f"%{search}%", f"%{search}%"))
    students = query(conn, """
        SELECT student_id, first_name, last_name FROM students ORDER BY first_name
    """)
    return render_template("contacts/list.html",
                           contacts=contacts, students=students, search=search)

@app.route("/contacts/add", methods=["POST"])
@login_required
@permission_required("write")
def contacts_add():
    conn = get_db()
    try:
        execute(conn, """
            INSERT INTO contact_info
            (student_id, guardian_name, relation, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.form["student_id"],
            request.form["guardian_name"],
            request.form.get("relation"),
            request.form.get("phone"),
            request.form.get("address"),
        ))
        flash("Contact added!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("contacts_list"))

@app.route("/contacts/edit/<int:cid>", methods=["GET", "POST"])
@login_required
@permission_required("update")
def contacts_edit(cid):
    conn    = get_db()
    contact = query_one(conn, """
        SELECT ci.*, s.first_name, s.last_name
        FROM contact_info ci
        JOIN students s ON ci.student_id = s.student_id
        WHERE ci.contact_id=%s
    """, (cid,))
    if not contact:
        abort(404)

    if request.method == "POST":
        try:
            execute(conn, """
                UPDATE contact_info
                SET guardian_name=%s, relation=%s, phone=%s, address=%s
                WHERE contact_id=%s
            """, (
                request.form["guardian_name"],
                request.form.get("relation"),
                request.form.get("phone"),
                request.form.get("address"),
                cid,
            ))
            flash("Contact updated!", "success")
            return redirect(url_for("contacts_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("contacts/edit.html", contact=contact)

@app.route("/contacts/delete/<int:cid>", methods=["POST"])
@login_required
@permission_required("delete")
def contacts_delete(cid):
    conn = get_db()
    try:
        execute(conn, "DELETE FROM contact_info WHERE contact_id=%s", (cid,))
        flash("Contact deleted!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("contacts_list"))

# ═════════════════════════════════════════════════════════════
# AUDIT LOGS  (superuser / logs permission only)
# ═════════════════════════════════════════════════════════════
@app.route("/logs")
@login_required
@permission_required("logs")
def logs_list():
    conn = get_db()

    # 1. Deleted students log
    del_logs = query(conn, """
        SELECT log_id, student_id, first_name, last_name,
               class_id, deleted_at, changed_by
        FROM deleted_student_log
        ORDER BY log_id DESC
        LIMIT 200
    """)

    # 2. Teacher update log
    tch_logs = query(conn, """
        SELECT log_id, teacher_id,
               old_name,  new_name,
               old_email, new_email,
               old_phone, new_phone,
               changed_at, changed_by
        FROM teacher_log_table
        ORDER BY log_id DESC
        LIMIT 200
    """)

    # 3. Student update log
    stu_update_logs = query(conn, """
        SELECT log_id, student_id,
               old_first_name, new_first_name,
               old_last_name,  new_last_name,
               old_class_id,   new_class_id,
               old_status,     new_status,
               changed_at,     changed_by
        FROM student_log_table
        ORDER BY log_id DESC
        LIMIT 200
    """)

    # 4. Teacher delete log
    tch_del_logs = query(conn, """
        SELECT log_id, teacher_id,
               name, email, phone, hire_date,
               deleted_at, changed_by
        FROM teacher_delete_log
        ORDER BY log_id DESC
        LIMIT 200
    """)

    # 5. Teacher insert log
    tch_ins_logs = query(conn, """
        SELECT log_id, teacher_id,
               name, email, phone, hire_date,
               inserted_at, inserted_by
        FROM teacher_insert_log
        ORDER BY log_id DESC
        LIMIT 200
    """)

    # 6. Student insert log
    stu_ins_logs = query(conn, """
        SELECT log_id, student_id,
               first_name, last_name,
               class_id, gender, admission_date,
               inserted_at, inserted_by
        FROM student_insert_log
        ORDER BY log_id DESC
        LIMIT 200
    """)

    return render_template(
        "logs/list.html",
        del_logs        = del_logs,
        tch_logs        = tch_logs,
        stu_update_logs = stu_update_logs,
        tch_del_logs    = tch_del_logs,
        tch_ins_logs    = tch_ins_logs,
        stu_ins_logs    = stu_ins_logs,
    )

# ═════════════════════════════════════════════════════════════
# RUN
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True, port=5000)