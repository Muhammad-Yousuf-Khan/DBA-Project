CREATE VIEW student_contact_details AS
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



CREATE VIEW student_complete_details AS
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
LEFT JOIN classes c ON s.class_id = c.class_id
LEFT JOIN teachers t ON c.class_incharge = t.teacher_id;



CREATE VIEW class_subject_teacher AS
SELECT 
    c.class_name,
    sub.subject_name,
    t.name AS teacher_name
FROM teacher_class_subject tcs
JOIN classes c ON tcs.class_id = c.class_id
JOIN subjects sub ON tcs.subject_id = sub.subject_id
JOIN teachers t ON tcs.teacher_id = t.teacher_id;


CREATE VIEW student_fee_details AS
SELECT 
    s.student_id,
    s.first_name,
    s.last_name,
    f.amount,
    f.due_date,
    f.paid_date,
    f.status
FROM students s
JOIN fees f ON s.student_id = f.student_id;


CREATE VIEW class_overview AS
SELECT 
    c.class_id,
    c.class_name,
    COUNT(s.student_id) AS total_students
FROM classes c
LEFT JOIN students s ON c.class_id = s.class_id
GROUP BY c.class_id, c.class_name;