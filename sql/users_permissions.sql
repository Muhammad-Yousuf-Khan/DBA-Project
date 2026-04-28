CREATE USER yousuf WITH LOGIN PASSWORD 'yousuf';
CREATE USER talha  WITH LOGIN PASSWORD 'talha';
CREATE USER umar   WITH LOGIN PASSWORD 'umar';


GRANT CONNECT ON DATABASE school TO yousuf, talha, umar;

GRANT USAGE ON SCHEMA public TO yousuf, talha, umar;

GRANT ALL PRIVILEGES ON TABLE
students,
teachers,
classes,
subjects,
teacher_class_subject,
fees,
contact_info
TO yousuf;

GRANT SELECT, INSERT, UPDATE ON TABLE
students,
teachers,
classes,
subjects,
teacher_class_subject,
fees,
contact_info
TO talha;

GRANT SELECT ON TABLE
students,
teachers,
classes,
subjects,
teacher_class_subject,
fees,
contact_info
TO umar;

-- for yousuf (full)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO yousuf;

-- for talha (needed for INSERT)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO talha;

-- umar does not need (only has)

