# pip install psycopg2-binary tabulate
# ─────────────────────────────────────────────────────────────

import psycopg2
import psycopg2.extras
from tabulate import tabulate
import getpass, sys, os

# ── ANSI Colours ──────────────────────────────────────────────
R="\033[0m"; BOLD="\033[1m"; RED="\033[91m"; GRN="\033[92m"
YLW="\033[93m"; CYN="\033[96m"; BLU="\033[94m"; MAG="\033[95m"

def c(t, col): return f"{col}{t}{R}"

# ── Role Permissions ──────────────────────────────────────────
ROLES = {
    "yousuf":   {"role": "admin",     "perms": ["read","write","update","delete"]},
    "talha":    {"role": "editor",    "perms": ["read","write","update"]},
    "umar":     {"role": "viewer",    "perms": ["read"]},
    "postgres": {"role": "superuser", "perms": ["read","write","update","delete","logs"]},
}

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "school"

# ── Globals ───────────────────────────────────────────────────
conn  = None
perms = []
role  = ""
uname = ""

# ─────────────────────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print(c("╔══════════════════════════════════════════════════════╗", CYN))
    print(c("║   🏫  School Management System  –  CLI Interface     ║", BOLD+CYN))
    print(c("╚══════════════════════════════════════════════════════╝", CYN))
    if uname:
        role_colours = {
            "superuser": YLW, "admin": GRN, "editor": BLU, "viewer": MAG
        }
        rc = role_colours.get(role, R)
        print(c(f"  Logged in as: {BOLD}{uname}{R}{CYN}  |  Role: ", CYN)
              + c(role.upper(), rc+BOLD))
        print(c(f"  Permissions : {', '.join(perms)}", CYN))
    print()

# ── FIXED pt() ── works with RealDictRow, dict, or plain lists ─
def pt(rows, headers=None):
    """
    Print rows as a pretty table.
    - rows: list of RealDictRow / dict / list
    - headers: None  → use dict keys automatically
               list  → use as column headers (converts rows to list-of-lists)
    """
    if not rows:
        print(c("  (No records found)", YLW))
        return

    # Convert RealDictRow → plain dict
    plain = [dict(r) for r in rows]

    if headers is None:
        # Auto-detect keys from first row
        print(tabulate(plain, headers="keys", tablefmt="rounded_outline"))
    elif isinstance(headers, list) and len(headers) > 0:
        # Caller gave explicit string headers
        # Check if it's a list of strings (not dict keys object)
        if isinstance(headers[0], str):
            # Convert dicts → list-of-lists using dict order
            keys = list(plain[0].keys())
            data = [[row.get(k) for k in keys] for row in plain]
            print(tabulate(data, headers=headers, tablefmt="rounded_outline"))
        else:
            # Fallback: just use keys
            print(tabulate(plain, headers="keys", tablefmt="rounded_outline"))
    else:
        # Empty headers or unknown → use keys
        print(tabulate(plain, headers="keys", tablefmt="rounded_outline"))

def inp(prompt, optional=False):
    tag = c(f"  ➤ {prompt} {'(opt) ' if optional else ''}: ", BLU)
    v   = input(tag).strip()
    return v or None

def ok(m):   print(c(f"\n  ✅  {m}\n", GRN))
def err(m):  print(c(f"\n  ❌  {m}\n", RED))
def info(m): print(c(f"\n  ℹ  {m}\n", CYN))

def confirm(msg):
    return input(c(f"  ⚠  {msg} [y/N]: ", YLW)).strip().lower() == "y"

def pause():
    input(c("\n  Press Enter to continue...", MAG))

def need(perm):
    if perm not in perms:
        err(f"Permission denied. '{perm}' required for your role ({role}).")
        pause()
        return False
    return True

def qry(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()

def qone(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()

def exe(sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
    conn.commit()

def menu(title, opts):
    banner()
    pad = 46 - len(title)
    print(c(f"  ── {title} {'─' * max(pad, 2)}", MAG))
    for i, o in enumerate(opts, 1):
        print(f"  {c(str(i), BOLD+CYN)}. {o}")
    print(f"  {c('0', BOLD+RED)}. ← Back / Exit")
    return input(c("\n  Choice: ", BLU)).strip()

# ─────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────
def login():
    global conn, perms, role, uname
    banner()
    print(c("  ── Database Login ──────────────────────────────", CYN))
    print(c("  Available users: yousuf / talha / umar / postgres\n", YLW))

    uname  = inp("Username") or "postgres"
    passwd = getpass.getpass(c("  ➤ Password: ", BLU))

    if uname not in ROLES:
        err("Unknown user. Choose from: yousuf / talha / umar / postgres")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=uname, password=passwd,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        role  = ROLES[uname]["role"]
        perms = ROLES[uname]["perms"]
        ok(f"Connected as {BOLD}{uname}{R}{GRN} (role: {role})")
        pause()
    except Exception as e:
        err(str(e))
        sys.exit(1)

# ─────────────────────────────────────────────────────────────
# STUDENTS
# ─────────────────────────────────────────────────────────────
def students():
    while True:
        ch = menu("STUDENTS 👨‍🎓", [
            "List all students",
            "Search student",
            "Add student          [write]",
            "Edit student         [update]  ← triggers audit log",
            "Delete student       [delete]  ← triggers audit log",
            "Student full view    (DB View)",
        ])
        if   ch == "1": _list_students()
        elif ch == "2": _search_students()
        elif ch == "3": _add_student()
        elif ch == "4": _edit_student()
        elif ch == "5": _delete_student()
        elif ch == "6": _student_view()
        elif ch == "0": break

def _list_students(where="", p=()):
    rows = qry("""
        SELECT s.student_id, s.first_name, s.last_name, s.gender,
               c.class_name, s.admission_date, s.status
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
    """ + where + " ORDER BY s.student_id", p)
    pt(rows, ["ID","First","Last","Gender","Class","Admitted","Status"])
    pause()

def _search_students():
    t = inp("Search name")
    if t:
        _list_students(
            " WHERE s.first_name ILIKE %s OR s.last_name ILIKE %s",
            (f"%{t}%", f"%{t}%")
        )

def _add_student():
    if not need("write"): return
    fn  = inp("First Name")
    ln  = inp("Last Name", True)
    dob = inp("Date of Birth YYYY-MM-DD", True)
    gen = inp("Gender (Male/Female)", True)
    cid = inp("Class ID", True)
    adm = inp("Admission Date YYYY-MM-DD", True)
    sts = inp("Status [active]") or "active"
    try:
        exe("""
            INSERT INTO students
            (first_name, last_name, date_of_birth, gender,
             class_id, admission_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (fn, ln, dob, gen, int(cid) if cid else None, adm, sts))
        ok("Student added. ✔ Insert trigger fired → student_insert_log")
    except Exception as e:
        err(e)
    pause()

def _edit_student():
    if not need("update"): return
    sid = inp("Student ID")
    if not sid: return
    r = qone("SELECT * FROM students WHERE student_id=%s", (int(sid),))
    if not r:
        err("Not found.")
        pause()
        return
    print(c("\n  Current record:", YLW))
    for k, v in r.items():
        print(c(f"    {k}: {v}", YLW))
    print(c("\n  (Press Enter to keep current value)", YLW))
    fields = [
        "first_name","last_name","date_of_birth",
        "gender","class_id","admission_date","status"
    ]
    vals = []
    for f in fields:
        cur = str(r[f]) if r[f] is not None else ""
        v   = input(c(f"  ➤ {f} [{cur}]: ", BLU)).strip()
        vals.append(v if v else r[f])
    try:
        exe("""
            UPDATE students
            SET first_name=%s, last_name=%s, date_of_birth=%s,
                gender=%s, class_id=%s, admission_date=%s, status=%s
            WHERE student_id=%s
        """, (*vals, int(sid)))
        ok("Student updated. ✔ Update trigger fired → student_log_table")
    except Exception as e:
        err(e)
    pause()

def _delete_student():
    if not need("delete"): return
    sid = inp("Student ID to delete")
    if not sid: return
    r = qone("""
        SELECT s.student_id, s.first_name, s.last_name,
               COALESCE(c.class_name, 'N/A') AS class_name
        FROM students s
        LEFT JOIN classes c ON s.class_id = c.class_id
        WHERE s.student_id = %s
    """, (int(sid),))
    if not r:
        err("Student not found.")
        pause()
        return
    print(c(f"\n  Student: {r['first_name']} {r['last_name']} "
            f"| Class: {r['class_name']}", YLW))
    if confirm(f"Delete student #{sid}? (trigger logs to deleted_student_log)"):
        try:
            exe("DELETE FROM students WHERE student_id=%s", (int(sid),))
            ok("Student deleted. ✔ Delete trigger fired → deleted_student_log")
        except Exception as e:
            err(e)
    pause()

def _student_view():
    sid = inp("Student ID (blank = all)", True)
    sql = "SELECT * FROM student_complete_details"
    p   = ()
    if sid:
        sql += " WHERE student_id=%s"
        p    = (int(sid),)
    rows = qry(sql, p)
    pt(rows)   # auto keys
    pause()

# ─────────────────────────────────────────────────────────────
# TEACHERS
# ─────────────────────────────────────────────────────────────
def teachers():
    while True:
        ch = menu("TEACHERS 👩‍🏫", [
            "List all teachers",
            "Add teacher          [write]   ← triggers audit log",
            "Edit teacher         [update]  ← triggers audit log",
            "Delete teacher       [delete]  ← triggers audit log",
            "View teacher audit logs  [logs / superuser]",
        ])
        if   ch == "1": _list_teachers()
        elif ch == "2": _add_teacher()
        elif ch == "3": _edit_teacher()
        elif ch == "4": _del_teacher()
        elif ch == "5": _teacher_log()
        elif ch == "0": break

def _list_teachers():
    rows = qry("""
        SELECT teacher_id, name, email, phone, hire_date
        FROM teachers
        ORDER BY teacher_id
    """)
    pt(rows, ["ID","Name","Email","Phone","Hire Date"])
    pause()

def _add_teacher():
    if not need("write"): return
    name  = inp("Full Name")
    email = inp("Email", True)
    phone = inp("Phone", True)
    hd    = inp("Hire Date YYYY-MM-DD", True)
    try:
        exe("""
            INSERT INTO teachers (name, email, phone, hire_date)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, hd))
        ok("Teacher added. ✔ Insert trigger fired → teacher_insert_log")
    except Exception as e:
        err(e)
    pause()

def _edit_teacher():
    if not need("update"): return
    tid = inp("Teacher ID")
    if not tid: return
    r = qone("SELECT * FROM teachers WHERE teacher_id=%s", (int(tid),))
    if not r:
        err("Not found.")
        pause()
        return
    print(c("\n  Current record:", YLW))
    for k, v in r.items():
        print(c(f"    {k}: {v}", YLW))
    print(c("\n  (Press Enter to keep current value)", YLW))
    fields = ["name","email","phone","hire_date"]
    vals   = []
    for f in fields:
        cur = str(r[f]) if r[f] is not None else ""
        v   = input(c(f"  ➤ {f} [{cur}]: ", BLU)).strip()
        vals.append(v if v else r[f])
    try:
        exe("""
            UPDATE teachers
            SET name=%s, email=%s, phone=%s, hire_date=%s
            WHERE teacher_id=%s
        """, (*vals, int(tid)))
        ok("Teacher updated. ✔ Update trigger fired → teacher_log_table")
    except Exception as e:
        err(e)
    pause()

def _del_teacher():
    if not need("delete"): return
    tid = inp("Teacher ID")
    if not tid: return
    r = qone("""
        SELECT teacher_id, name, email
        FROM teachers WHERE teacher_id=%s
    """, (int(tid),))
    if not r:
        err("Teacher not found.")
        pause()
        return
    print(c(f"\n  Teacher: {r['name']} | Email: {r['email']}", YLW))
    if confirm(f"Delete teacher #{tid}? (trigger logs to teacher_delete_log)"):
        try:
            exe("DELETE FROM teachers WHERE teacher_id=%s", (int(tid),))
            ok("Teacher deleted. ✔ Delete trigger fired → teacher_delete_log")
        except Exception as e:
            err(e)
    pause()

def _teacher_log():
    if not need("logs"): return
    while True:
        ch = menu("TEACHER AUDIT LOGS 📋", [
            "Teacher Insert Log   (teacher_insert_log)",
            "Teacher Update Log   (teacher_log_table)",
            "Teacher Delete Log   (teacher_delete_log)",
        ])
        if ch == "1":
            rows = qry("""
                SELECT log_id, teacher_id, name, email,
                       phone, hire_date, inserted_at, inserted_by
                FROM teacher_insert_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)   # auto keys
            pause()
        elif ch == "2":
            rows = qry("""
                SELECT log_id, teacher_id,
                       old_name,  new_name,
                       old_email, new_email,
                       old_phone, new_phone,
                       changed_at, changed_by
                FROM teacher_log_table
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)   # auto keys
            pause()
        elif ch == "3":
            rows = qry("""
                SELECT log_id, teacher_id, name, email,
                       phone, hire_date, deleted_at, changed_by
                FROM teacher_delete_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)   # auto keys
            pause()
        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# CLASSES
# ─────────────────────────────────────────────────────────────
def classes():
    while True:
        ch = menu("CLASSES 🏛️", [
            "List classes",
            "Class overview  (student counts)",
            "Add class       [write]",
            "Edit class      [update]",
            "Delete class    [delete]",
        ])
        if   ch == "1": _list_classes()
        elif ch == "2": _class_overview()
        elif ch == "3": _add_class()
        elif ch == "4": _edit_class()
        elif ch == "5": _del_class()
        elif ch == "0": break

def _list_classes():
    rows = qry("""
        SELECT c.class_id, c.class_name,
               COALESCE(t.name,'—') AS incharge
        FROM classes c
        LEFT JOIN teachers t ON c.class_incharge = t.teacher_id
        ORDER BY c.class_id
    """)
    pt(rows, ["ID","Class","Incharge"])
    pause()

def _class_overview():
    rows = qry("SELECT * FROM class_overview ORDER BY class_id")
    pt(rows, ["ID","Class","Total Students"])
    pause()

def _add_class():
    if not need("write"): return
    name = inp("Class Name")
    inc  = inp("Incharge Teacher ID", True)
    try:
        exe("INSERT INTO classes(class_name,class_incharge) VALUES(%s,%s)",
            (name, int(inc) if inc else None))
        ok("Class added.")
    except Exception as e:
        err(e)
    pause()

def _edit_class():
    if not need("update"): return
    cid = inp("Class ID")
    if not cid: return
    r = qone("SELECT * FROM classes WHERE class_id=%s", (int(cid),))
    if not r:
        err("Not found.")
        pause()
        return
    name = input(c(f"  ➤ class_name [{r['class_name']}]: ", BLU)).strip() \
           or r['class_name']
    inc  = input(c(f"  ➤ class_incharge [{r['class_incharge']}]: ", BLU)).strip()
    inc  = int(inc) if inc else r['class_incharge']
    try:
        exe("UPDATE classes SET class_name=%s, class_incharge=%s WHERE class_id=%s",
            (name, inc, int(cid)))
        ok("Class updated.")
    except Exception as e:
        err(e)
    pause()

def _del_class():
    if not need("delete"): return
    cid = inp("Class ID")
    if not cid: return
    if confirm(f"Delete class #{cid}? (students in it will have class set to NULL)"):
        try:
            exe("DELETE FROM classes WHERE class_id=%s", (int(cid),))
            ok("Class deleted.")
        except Exception as e:
            err(e)
    pause()

# ─────────────────────────────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────────────────────────────
def subjects():
    while True:
        ch = menu("SUBJECTS 📖", [
            "List subjects",
            "Add subject    [write]",
            "Edit subject   [update]",
            "Delete subject [delete]",
        ])
        if ch == "1":
            rows = qry("SELECT * FROM subjects ORDER BY subject_id")
            pt(rows, ["ID","Subject"])
            pause()

        elif ch == "2":
            if not need("write"): continue
            n = inp("Subject Name")
            if not n: continue
            try:
                exe("INSERT INTO subjects(subject_name) VALUES(%s)", (n,))
                ok("Subject added.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "3":
            if not need("update"): continue
            sid = inp("Subject ID")
            if not sid: continue
            r = qone("SELECT * FROM subjects WHERE subject_id=%s", (int(sid),))
            if not r:
                err("Not found.")
                pause()
                continue
            n = input(c(f"  ➤ subject_name [{r['subject_name']}]: ", BLU)).strip() \
                or r['subject_name']
            try:
                exe("UPDATE subjects SET subject_name=%s WHERE subject_id=%s",
                    (n, int(sid)))
                ok("Subject updated.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "4":
            if not need("delete"): continue
            sid = inp("Subject ID")
            if not sid: continue
            if confirm(f"Delete subject #{sid}?"):
                try:
                    exe("DELETE FROM subjects WHERE subject_id=%s", (int(sid),))
                    ok("Subject deleted.")
                except Exception as e:
                    err(e)
            pause()

        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# ASSIGNMENTS
# ─────────────────────────────────────────────────────────────
def assignments():
    while True:
        ch = menu("ASSIGNMENTS 🔗", [
            "List all assignments",
            "Add assignment     [write]",
            "Remove assignment  [delete]",
            "Class-Subject-Teacher report  (DB View)",
        ])
        if ch == "1":
            rows = qry("""
                SELECT tcs.id, t.name AS teacher,
                       c.class_name, s.subject_name
                FROM teacher_class_subject tcs
                JOIN teachers t ON tcs.teacher_id = t.teacher_id
                JOIN classes  c ON tcs.class_id   = c.class_id
                JOIN subjects s ON tcs.subject_id = s.subject_id
                ORDER BY tcs.id
            """)
            pt(rows, ["ID","Teacher","Class","Subject"])
            pause()

        elif ch == "2":
            if not need("write"): continue
            tid = inp("Teacher ID")
            cid = inp("Class ID")
            sid = inp("Subject ID")
            if not all([tid, cid, sid]): continue
            try:
                exe("""
                    INSERT INTO teacher_class_subject
                    (teacher_id, class_id, subject_id)
                    VALUES(%s,%s,%s)
                """, (int(tid), int(cid), int(sid)))
                ok("Assignment added.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "3":
            if not need("delete"): continue
            aid = inp("Assignment ID")
            if not aid: continue
            if confirm(f"Remove assignment #{aid}?"):
                try:
                    exe("DELETE FROM teacher_class_subject WHERE id=%s", (int(aid),))
                    ok("Assignment removed.")
                except Exception as e:
                    err(e)
            pause()

        elif ch == "4":
            rows = qry("SELECT * FROM class_subject_teacher ORDER BY class_name")
            pt(rows)   # auto keys
            pause()

        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# FEES
# ─────────────────────────────────────────────────────────────
def fees():
    while True:
        ch = menu("FEES 💰", [
            "List all fees",
            "List unpaid fees",
            "List paid fees",
            "Add fee record  [write]",
            "Mark fee paid   [update]",
            "Delete fee      [delete]",
        ])

        def _show(where="", p=()):
            rows = qry(f"""
                SELECT f.fee_id, s.student_id,
                       s.first_name, s.last_name,
                       f.amount, f.due_date, f.paid_date, f.status
                FROM fees f
                JOIN students s ON f.student_id = s.student_id
                {where}
                ORDER BY f.fee_id
            """, p)
            pt(rows, ["Fee ID","Stu ID","First","Last",
                      "Amount","Due","Paid","Status"])
            pause()

        if   ch == "1": _show()
        elif ch == "2": _show("WHERE f.status='unpaid'")
        elif ch == "3": _show("WHERE f.status='paid'")

        elif ch == "4":
            if not need("write"): continue
            sid = inp("Student ID")
            amt = inp("Amount")
            dd  = inp("Due Date YYYY-MM-DD", True)
            if not sid or not amt: continue
            try:
                exe("""
                    INSERT INTO fees(student_id, amount, due_date, status)
                    VALUES(%s,%s,%s,'unpaid')
                """, (int(sid), float(amt), dd))
                ok("Fee record added.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "5":
            if not need("update"): continue
            fid = inp("Fee ID")
            if not fid: continue
            try:
                exe("""
                    UPDATE fees
                    SET status='paid', paid_date=CURRENT_DATE
                    WHERE fee_id=%s
                """, (int(fid),))
                ok("Fee marked as paid.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "6":
            if not need("delete"): continue
            fid = inp("Fee ID")
            if not fid: continue
            if confirm(f"Delete fee #{fid}?"):
                try:
                    exe("DELETE FROM fees WHERE fee_id=%s", (int(fid),))
                    ok("Fee record deleted.")
                except Exception as e:
                    err(e)
            pause()

        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# CONTACTS
# ─────────────────────────────────────────────────────────────
def contacts():
    while True:
        ch = menu("CONTACTS 📞", [
            "List all contacts",
            "Search by student / guardian",
            "Add contact    [write]",
            "Edit contact   [update]",
            "Delete contact [delete]",
        ])
        if ch == "1":
            rows = qry("""
                SELECT ci.contact_id,
                       s.first_name, s.last_name,
                       ci.guardian_name, ci.relation,
                       ci.phone, ci.address
                FROM contact_info ci
                JOIN students s ON ci.student_id = s.student_id
                ORDER BY ci.contact_id
            """)
            pt(rows, ["ID","First","Last","Guardian","Relation","Phone","Address"])
            pause()

        elif ch == "2":
            t = inp("Search term")
            if not t: continue
            rows = qry("""
                SELECT ci.contact_id,
                       s.first_name, s.last_name,
                       ci.guardian_name, ci.phone
                FROM contact_info ci
                JOIN students s ON ci.student_id = s.student_id
                WHERE ci.guardian_name ILIKE %s
                   OR s.first_name    ILIKE %s
                   OR s.last_name     ILIKE %s
            """, (f"%{t}%", f"%{t}%", f"%{t}%"))
            pt(rows, ["ID","First","Last","Guardian","Phone"])
            pause()

        elif ch == "3":
            if not need("write"): continue
            sid  = inp("Student ID")
            gn   = inp("Guardian Name")
            rel  = inp("Relation (Father/Mother/Other)", True)
            ph   = inp("Phone", True)
            addr = inp("Address", True)
            if not sid or not gn: continue
            try:
                exe("""
                    INSERT INTO contact_info
                    (student_id, guardian_name, relation, phone, address)
                    VALUES(%s,%s,%s,%s,%s)
                """, (int(sid), gn, rel, ph, addr))
                ok("Contact added.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "4":
            if not need("update"): continue
            cid = inp("Contact ID")
            if not cid: continue
            r = qone("SELECT * FROM contact_info WHERE contact_id=%s", (int(cid),))
            if not r:
                err("Not found.")
                pause()
                continue
            gn   = input(c(f"  ➤ guardian_name [{r['guardian_name']}]: ",
                           BLU)).strip() or r['guardian_name']
            rel  = input(c(f"  ➤ relation [{r['relation']}]: ",
                           BLU)).strip()  or r['relation']
            ph   = input(c(f"  ➤ phone [{r['phone']}]: ",
                           BLU)).strip()  or r['phone']
            addr = input(c(f"  ➤ address [{r['address']}]: ",
                           BLU)).strip()  or r['address']
            try:
                exe("""
                    UPDATE contact_info
                    SET guardian_name=%s, relation=%s,
                        phone=%s, address=%s
                    WHERE contact_id=%s
                """, (gn, rel, ph, addr, int(cid)))
                ok("Contact updated.")
            except Exception as e:
                err(e)
            pause()

        elif ch == "5":
            if not need("delete"): continue
            cid = inp("Contact ID")
            if not cid: continue
            if confirm(f"Delete contact #{cid}?"):
                try:
                    exe("DELETE FROM contact_info WHERE contact_id=%s", (int(cid),))
                    ok("Contact deleted.")
                except Exception as e:
                    err(e)
            pause()

        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# AUDIT LOGS  (superuser / postgres only)
# ─────────────────────────────────────────────────────────────
def audit_logs():
    if not need("logs"): return
    while True:
        ch = menu("AUDIT LOGS 📋  [SUPERUSER]", [
            "Student Insert Log   (student_insert_log)",
            "Student Update Log   (student_log_table)",
            "Student Delete Log   (deleted_student_log)",
            "Teacher Insert Log   (teacher_insert_log)",
            "Teacher Update Log   (teacher_log_table)",
            "Teacher Delete Log   (teacher_delete_log)",
            "Show ALL logs summary",
        ])

        # ── Student Insert Log ────────────────────────────────
        if ch == "1":
            rows = qry("""
                SELECT log_id, student_id,
                       first_name, last_name,
                       class_id, gender, admission_date,
                       inserted_at, inserted_by
                FROM student_insert_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── Student Update Log ────────────────────────────────
        elif ch == "2":
            rows = qry("""
                SELECT log_id, student_id,
                       old_first_name, new_first_name,
                       old_last_name,  new_last_name,
                       old_class_id,   new_class_id,
                       old_status,     new_status,
                       changed_at,     changed_by
                FROM student_log_table
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── Student Delete Log ────────────────────────────────
        elif ch == "3":
            rows = qry("""
                SELECT log_id, student_id,
                       first_name, last_name,
                       class_id, deleted_at, changed_by
                FROM deleted_student_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── Teacher Insert Log ────────────────────────────────
        elif ch == "4":
            rows = qry("""
                SELECT log_id, teacher_id,
                       name, email, phone, hire_date,
                       inserted_at, inserted_by
                FROM teacher_insert_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── Teacher Update Log ────────────────────────────────
        elif ch == "5":
            rows = qry("""
                SELECT log_id, teacher_id,
                       old_name,  new_name,
                       old_email, new_email,
                       old_phone, new_phone,
                       changed_at, changed_by
                FROM teacher_log_table
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── Teacher Delete Log ────────────────────────────────
        elif ch == "6":
            rows = qry("""
                SELECT log_id, teacher_id,
                       name, email, phone, hire_date,
                       deleted_at, changed_by
                FROM teacher_delete_log
                ORDER BY log_id DESC LIMIT 100
            """)
            pt(rows)
            pause()

        # ── All Logs Summary ──────────────────────────────────
        elif ch == "7":
            banner()
            print(c("  ── AUDIT LOG SUMMARY ─────────────────────────────", MAG))
            summary = qry("""
                SELECT
                    (SELECT COUNT(*) FROM student_insert_log)  AS stu_inserts,
                    (SELECT COUNT(*) FROM student_log_table)   AS stu_updates,
                    (SELECT COUNT(*) FROM deleted_student_log) AS stu_deletes,
                    (SELECT COUNT(*) FROM teacher_insert_log)  AS tch_inserts,
                    (SELECT COUNT(*) FROM teacher_log_table)   AS tch_updates,
                    (SELECT COUNT(*) FROM teacher_delete_log)  AS tch_deletes
            """)
            if summary:
                row  = dict(summary[0])
                data = [
                    ["Student Inserts", row["stu_inserts"], "student_insert_log"],
                    ["Student Updates", row["stu_updates"], "student_log_table"],
                    ["Student Deletes", row["stu_deletes"], "deleted_student_log"],
                    ["Teacher Inserts", row["tch_inserts"], "teacher_insert_log"],
                    ["Teacher Updates", row["tch_updates"], "teacher_log_table"],
                    ["Teacher Deletes", row["tch_deletes"], "teacher_delete_log"],
                ]
                print(tabulate(
                    data,
                    headers=["Event Type", "Count", "Log Table"],
                    tablefmt="rounded_outline"
                ))
            pause()

        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# REPORTS  (DB Views)
# ─────────────────────────────────────────────────────────────
def reports():
    while True:
        ch = menu("REPORTS & DB VIEWS 📊", [
            "Student complete details",
            "Student contact details",
            "Class overview",
            "Class-Subject-Teacher map",
            "Student fee details",
        ])

        # Map choice → view name only (pt() will auto-read keys)
        views = {
            "1": "student_complete_details",
            "2": "student_contact_details",
            "3": "class_overview",
            "4": "class_subject_teacher",
            "5": "student_fee_details",
        }

        if ch in views:
            rows = qry(f"SELECT * FROM {views[ch]}")
            pt(rows)   # ← auto keys, no manual headers needed
            pause()
        elif ch == "0":
            break

# ─────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────
def main():
    login()
    while True:
        # Build dynamic menu
        opts = [
            " Students",
            " Teachers",
            " Classes",
            " Subjects",
            " Assignments",
            " Fees",
            " Contacts",
            " Reports & Views",
        ]
        has_logs = "logs" in perms
        if has_logs:
            opts.append(" Audit Logs  [SUPERUSER]")
        opts.append("Exit")

        ch = menu("MAIN MENU", opts)

        # Fixed exit number: 9 without logs, 10 with logs
        exit_num = "10" if has_logs else "9"

        if   ch == "1": students()
        elif ch == "2": teachers()
        elif ch == "3": classes()
        elif ch == "4": subjects()
        elif ch == "5": assignments()
        elif ch == "6": fees()
        elif ch == "7": contacts()
        elif ch == "8": reports()
        elif ch == "9" and has_logs:
            audit_logs()
        elif ch == exit_num or ch == "0":
            if confirm("Exit the application?"):
                if conn:
                    conn.close()
                print(c("\n  Goodbye! 👋\n", GRN))
                sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if conn:
            conn.close()
        print(c("\n\n  Interrupted. Goodbye! 👋\n", YLW))
        sys.exit(0)