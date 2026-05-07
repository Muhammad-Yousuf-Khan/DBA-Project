-- ============================================================
-- TABLE CREATION
-- ============================================================

-- 1. Teachers
CREATE TABLE teachers (
    teacher_id  SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE,
    phone       VARCHAR(20),
    hire_date   DATE
);

-- 2. Classes
CREATE TABLE classes (
    class_id      SERIAL PRIMARY KEY,
    class_name    VARCHAR(50) NOT NULL,
    class_incharge INT,
    CONSTRAINT fk_class_incharge
        FOREIGN KEY (class_incharge)
        REFERENCES teachers(teacher_id)
        ON DELETE SET NULL
);

-- 3. Students
CREATE TABLE students (
    student_id     SERIAL PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50),
    date_of_birth  DATE,
    gender         VARCHAR(10),
    class_id       INT,
    admission_date DATE,
    status         VARCHAR(20) DEFAULT 'active',
    CONSTRAINT fk_student_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
        ON DELETE SET NULL
);

-- 4. Subjects
CREATE TABLE subjects (
    subject_id   SERIAL PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL
);

-- 5. Teacher-Class-Subject Mapping
CREATE TABLE teacher_class_subject (
    id         SERIAL PRIMARY KEY,
    teacher_id INT NOT NULL,
    class_id   INT NOT NULL,
    subject_id INT NOT NULL,
    CONSTRAINT fk_tcs_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tcs_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_tcs_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
        ON DELETE CASCADE,
    CONSTRAINT unique_assignment
        UNIQUE (teacher_id, class_id, subject_id)
);

-- 6. Fees
CREATE TABLE fees (
    fee_id     SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    amount     NUMERIC(10,2) NOT NULL,
    due_date   DATE,
    paid_date  DATE,
    status     VARCHAR(20) DEFAULT 'unpaid',
    CONSTRAINT fk_fee_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);

-- 7. Contact Info
CREATE TABLE contact_info (
    contact_id    SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    guardian_name VARCHAR(100) NOT NULL,
    relation      VARCHAR(50),
    phone         VARCHAR(20),
    address       TEXT,
    CONSTRAINT fk_contact_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);

-- 8. Deleted Student Log 
CREATE TABLE deleted_student_log (
    log_id     SERIAL PRIMARY KEY,
    student_id INT,
    first_name VARCHAR(50),
    last_name  VARCHAR(50),
    class_id   INT,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who delete
);

-- 9. Teacher Update Log
CREATE TABLE teacher_log_table (
    log_id     SERIAL PRIMARY KEY,
    teacher_id INT,
    old_name   VARCHAR(100),
    new_name   VARCHAR(100),
    old_email  VARCHAR(100),
    new_email  VARCHAR(100),
    old_phone  VARCHAR(20),
    new_phone  VARCHAR(20),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who updated
);

-- ============================================================
-- AUDIT & Logs TABLES 
-- ============================================================

-- 10. Student Update Log
CREATE TABLE student_log_table (
    log_id          SERIAL PRIMARY KEY,
    student_id      INT,
    old_first_name  VARCHAR(50),
    new_first_name  VARCHAR(50),
    old_last_name   VARCHAR(50),
    new_last_name   VARCHAR(50),
    old_class_id    INT,
    new_class_id    INT,
    old_status      VARCHAR(20),
    new_status      VARCHAR(20),
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by      VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who updated
);

-- 11. Teacher Delete Log
CREATE TABLE teacher_delete_log (
    log_id     SERIAL PRIMARY KEY,
    teacher_id INT,
    name       VARCHAR(100),
    email      VARCHAR(100),
    phone      VARCHAR(20),
    hire_date  DATE,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who deleted
);

-- 12. Teacher Insert Log
CREATE TABLE teacher_insert_log (
    log_id      SERIAL PRIMARY KEY,
    teacher_id  INT,
    name        VARCHAR(100),
    email       VARCHAR(100),
    phone       VARCHAR(20),
    hire_date   DATE,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inserted_by VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who inserted
);

-- 13. Student Insert Log
CREATE TABLE student_insert_log (
    log_id        SERIAL PRIMARY KEY,
    student_id    INT,
    first_name    VARCHAR(50),
    last_name     VARCHAR(50),
    class_id      INT,
    gender        VARCHAR(10),
    admission_date DATE,
    inserted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inserted_by   VARCHAR(100) DEFAULT CURRENT_USER  -- Tracks who inserted
);

-- ============================================================
  -----  DATA INSERTION
-- ============================================================

-- Teachers
INSERT INTO teachers (name, email, phone, hire_date)
SELECT
    'Teacher ' || i,
    'teacher' || i || '@school.com',
    '0300' || LPAD(i::TEXT, 7, '0'),
    CURRENT_DATE - (i * INTERVAL '30 days')
FROM generate_series(1, 10) AS i;

-- Classes
INSERT INTO classes (class_name, class_incharge) VALUES
('Grade 1', 1),
('Grade 2', 2),
('Grade 3', 3),
('Grade 4', 4),
('Grade 5', 5);

-- Subjects
INSERT INTO subjects (subject_name) VALUES
('Mathematics'),
('English'),
('Science'),
('Urdu'),
('Computer'),
('Islamiyat');

-- Teacher-Class-Subject Mapping
INSERT INTO teacher_class_subject (teacher_id, class_id, subject_id)
SELECT
    (s % 10) + 1 AS teacher_id,
    c.class_id,
    s           AS subject_id
FROM classes c
CROSS JOIN generate_series(1, 6) AS s;

-- Students
INSERT INTO students (
    first_name, last_name, date_of_birth,
    gender, class_id, admission_date, status
)
SELECT
    'Student'  || s,
    'Class'    || c.class_id,
    DATE '2010-01-01' + (s * INTERVAL '30 days'),
    CASE WHEN s % 2 = 0 THEN 'Male' ELSE 'Female' END,
    c.class_id,
    CURRENT_DATE - (s * INTERVAL '10 days'),
    'active'
FROM classes c
CROSS JOIN generate_series(1, 50) AS s;

-- Fees
INSERT INTO fees (student_id, amount, due_date, paid_date, status)
SELECT
    student_id,
    5000.00,
    CURRENT_DATE + INTERVAL '10 days',
    NULL,
    'unpaid'
FROM students;

-- Contact Info
INSERT INTO contact_info (student_id, guardian_name, relation, phone, address)
SELECT
    student_id,
    'Guardian of Student ' || student_id,
    CASE WHEN student_id % 2 = 0 THEN 'Father' ELSE 'Mother' END,
    '0312' || LPAD(student_id::TEXT, 7, '0'),
    'Karachi, Pakistan'
FROM students;

-- ============================================================
--              VIEWS
-- ============================================================

-- View 1: Student Contact Details
CREATE OR REPLACE VIEW student_contact_details AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    c.guardian_name,
    c.relation,
    c.phone,
    c.address
FROM students s
JOIN contact_info c ON s.student_id = c.student_id;

-- View 2: Student Complete Details
CREATE OR REPLACE VIEW student_complete_details AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    s.gender,
    s.date_of_birth,
    s.admission_date,
    s.status,
    c.class_name,
    t.name AS class_incharge
FROM students s
LEFT JOIN classes  c ON s.class_id        = c.class_id
LEFT JOIN teachers t ON c.class_incharge  = t.teacher_id;

-- View 3: Class-Subject-Teacher Mapping
CREATE OR REPLACE VIEW class_subject_teacher AS
SELECT
    c.class_name,
    sub.subject_name,
    t.name AS teacher_name
FROM teacher_class_subject tcs
JOIN classes  c   ON tcs.class_id   = c.class_id
JOIN subjects sub ON tcs.subject_id = sub.subject_id
JOIN teachers t   ON tcs.teacher_id = t.teacher_id;

-- View 4: Student Fee Details
CREATE OR REPLACE VIEW student_fee_details AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    f.fee_id,
    f.amount,
    f.due_date,
    f.paid_date,
    f.status
FROM students s
JOIN fees f ON s.student_id = f.student_id;

-- View 5: Class Overview
CREATE OR REPLACE VIEW class_overview AS
SELECT
    c.class_id,
    c.class_name,
    COUNT(s.student_id) AS total_students
FROM classes c
LEFT JOIN students s ON c.class_id = s.class_id
GROUP BY c.class_id, c.class_name;

-- ============================================================
--  TRIGGER FUNCTIONS & TRIGGERS
-- ============================================================

-- 1. Log Deleted Student 
CREATE OR REPLACE FUNCTION log_deleted_student()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO deleted_student_log (
        student_id, first_name, last_name, class_id, deleted_at, changed_by
    )
    VALUES (
        OLD.student_id, OLD.first_name, OLD.last_name,
        OLD.class_id, CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN OLD;
END;
$$;

-- 2. Log Teacher Update 
CREATE OR REPLACE FUNCTION log_teacher_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO teacher_log_table (
        teacher_id,
        old_name,  new_name,
        old_email, new_email,
        old_phone, new_phone,
        changed_at, changed_by
    )
    VALUES (
        OLD.teacher_id,
        OLD.name,  NEW.name,
        OLD.email, NEW.email,
        OLD.phone, NEW.phone,
        CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN NEW;
END;
$$;

-- 3. Log Student Update 
CREATE OR REPLACE FUNCTION log_student_update()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO student_log_table (
        student_id,
        old_first_name, new_first_name,
        old_last_name,  new_last_name,
        old_class_id,   new_class_id,
        old_status,     new_status,
        changed_at,     changed_by
    )
    VALUES (
        OLD.student_id,
        OLD.first_name, NEW.first_name,
        OLD.last_name,  NEW.last_name,
        OLD.class_id,   NEW.class_id,
        OLD.status,     NEW.status,
        CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN NEW;
END;
$$;

-- 4. Log Deleted Teacher 
CREATE OR REPLACE FUNCTION log_deleted_teacher()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO teacher_delete_log (
        teacher_id, name, email, phone, hire_date,
        deleted_at, changed_by
    )
    VALUES (
        OLD.teacher_id,
        OLD.name,
        OLD.email,
        OLD.phone,
        OLD.hire_date,
        CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN OLD;
END;
$$;

-- 5. Log Inserted Teacher 
CREATE OR REPLACE FUNCTION log_inserted_teacher()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO teacher_insert_log (
        teacher_id, name, email, phone, hire_date,
        inserted_at, inserted_by
    )
    VALUES (
        NEW.teacher_id,
        NEW.name,
        NEW.email,
        NEW.phone,
        NEW.hire_date,
        CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN NEW;
END;
$$;

-- 6. Log Inserted Student 
CREATE OR REPLACE FUNCTION log_inserted_student()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO student_insert_log (
        student_id, first_name, last_name,
        class_id, gender, admission_date,
        inserted_at, inserted_by
    )
    VALUES (
        NEW.student_id,
        NEW.first_name,
        NEW.last_name,
        NEW.class_id,
        NEW.gender,
        NEW.admission_date,
        CURRENT_TIMESTAMP, CURRENT_USER
    );
    RETURN NEW;
END;
$$;

-- ============================================================
--              TRIGGERS
-- ============================================================

-- Drop old triggers if they exist to avoid conflicts
---DROP TRIGGER IF EXISTS trg_student_delete_log  ON students;
---DROP TRIGGER IF EXISTS trg_teacher_update_log  ON teachers;

-- Students
CREATE TRIGGER trg_student_delete_log
AFTER DELETE ON students
FOR EACH ROW EXECUTE FUNCTION log_deleted_student();

CREATE TRIGGER trg_student_update_log
AFTER UPDATE ON students
FOR EACH ROW EXECUTE FUNCTION log_student_update();

CREATE TRIGGER trg_student_insert_log
AFTER INSERT ON students
FOR EACH ROW EXECUTE FUNCTION log_inserted_student();

-- Teachers
CREATE TRIGGER trg_teacher_update_log
AFTER UPDATE ON teachers
FOR EACH ROW EXECUTE FUNCTION log_teacher_update();

CREATE TRIGGER trg_teacher_delete_log
AFTER DELETE ON teachers
FOR EACH ROW EXECUTE FUNCTION log_deleted_teacher();

CREATE TRIGGER trg_teacher_insert_log
AFTER INSERT ON teachers
FOR EACH ROW EXECUTE FUNCTION log_inserted_teacher();

-- ============================================================
--     USER CREATION & PRIVILEGES
-- ============================================================

-- Create Users (run as superuser)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'yousuf') THEN
        CREATE USER yousuf WITH LOGIN PASSWORD 'yousuf';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'talha') THEN
        CREATE USER talha WITH LOGIN PASSWORD 'talha';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'umar') THEN
        CREATE USER umar WITH LOGIN PASSWORD 'umar';
    END IF;
END
$$;

-- Connect Privileges
GRANT CONNECT ON DATABASE school TO yousuf, talha, umar;
GRANT USAGE  ON SCHEMA public   TO yousuf, talha, umar;

-- ---- YOUSUF: Full Admin Access----
GRANT ALL PRIVILEGES ON TABLE
    students, teachers, classes, subjects,
    teacher_class_subject, fees, contact_info
TO yousuf;

-- ---- TALHA: Read + Write (no delete) on base tables only ----
GRANT SELECT, INSERT, UPDATE ON TABLE
    students, teachers, classes, subjects,
    teacher_class_subject, fees, contact_info
TO talha;

-- ---- UMAR: Read Only (all tables) ----
GRANT SELECT ON TABLE
    students, teachers, classes, subjects,
    teacher_class_subject, fees, contact_info,
    deleted_student_log, teacher_log_table,
    student_log_table, teacher_delete_log, teacher_insert_log, student_insert_log
TO umar;

-- ---- Views: All users can read ----
GRANT SELECT ON
    student_contact_details,
    student_complete_details,
    class_subject_teacher,
    student_fee_details,
    class_overview
TO yousuf, talha, umar;

-- ---- Sequences ----
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO yousuf;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO talha;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO umar;