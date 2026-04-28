-- 1. Teachers
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    hire_date DATE
);

-- 2. Classes
CREATE TABLE classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    class_incharge INT,
    CONSTRAINT fk_class_incharge
        FOREIGN KEY (class_incharge)
        REFERENCES teachers(teacher_id)
        ON DELETE SET NULL
);

-- 3. Students
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(10),
    class_id INT,
    admission_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    CONSTRAINT fk_student_class
        FOREIGN KEY (class_id)
        REFERENCES classes(class_id)
        ON DELETE SET NULL
);

-- 4. Subjects
CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL
);

-- 5. Teacher-Class-Subject Mapping
CREATE TABLE teacher_class_subject (
    id SERIAL PRIMARY KEY,
    teacher_id INT NOT NULL,
    class_id INT NOT NULL,
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
    fee_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    due_date DATE,
    paid_date DATE,
    status VARCHAR(20) DEFAULT 'unpaid',
    CONSTRAINT fk_fee_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);

-- 7. Contact Info
CREATE TABLE contact_info (
    contact_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    guardian_name VARCHAR(100) NOT NULL,
    relation VARCHAR(50),
    phone VARCHAR(20),
    address TEXT,
    CONSTRAINT fk_contact_student
        FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);

--------------------------------------------------------------

INSERT INTO teachers (name, email, phone, hire_date)
SELECT 
    'Teacher ' || i,
    'teacher' || i || '@school.com',
    '0300' || LPAD(i::text, 7, '0'),
    CURRENT_DATE - (i * INTERVAL '30 days')
FROM generate_series(1, 10) AS i;


INSERT INTO classes (class_name, class_incharge)
VALUES
('Grade 1', 1),
('Grade 2', 2),
('Grade 3', 3),
('Grade 4', 4),
('Grade 5', 5);


INSERT INTO subjects (subject_name)
VALUES
('Mathematics'),
('English'),
('Science'),
('Urdu'),
('Computer'),
('Islamiyat');


INSERT INTO teacher_class_subject (teacher_id, class_id, subject_id)
SELECT 
    (s % 10) + 1 AS teacher_id,
    c.class_id,
    s AS subject_id
FROM classes c
CROSS JOIN generate_series(1, 6) AS s;



INSERT INTO students (
    first_name, last_name, date_of_birth, gender, 
    class_id, admission_date, status
)
SELECT
    'Student' || s,
    'Class' || c.class_id,
    DATE '2010-01-01' + (s * INTERVAL '30 days'),
    CASE WHEN s % 2 = 0 THEN 'Male' ELSE 'Female' END,
    c.class_id,
    CURRENT_DATE - (s * INTERVAL '10 days'),
    'active'
FROM classes c
CROSS JOIN generate_series(1, 50) AS s;




INSERT INTO fees (student_id, amount, due_date, paid_date, status)
SELECT
    student_id,
    5000.00,
    CURRENT_DATE + INTERVAL '10 days',
    NULL,
    'unpaid'
FROM students;



INSERT INTO contact_info (
    student_id, guardian_name, relation, phone, address
)
SELECT
    student_id,
    'Guardian of Student ' || student_id,
    CASE WHEN student_id % 2 = 0 THEN 'Father' ELSE 'Mother' END,
    '0312' || LPAD(student_id::text, 7, '0'),
    'Karachi, Pakistan'
FROM students;

