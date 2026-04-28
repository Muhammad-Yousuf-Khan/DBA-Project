CREATE TABLE deleted_student_log (
    log_id SERIAL PRIMARY KEY,
    student_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    class_id INT,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION log_deleted_student()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO deleted_student_log (
        student_id,
        first_name,
        last_name,
        class_id,
        deleted_at
    )
    VALUES (
        OLD.student_id,
        OLD.first_name,
        OLD.last_name,
        OLD.class_id,
        CURRENT_TIMESTAMP
    );

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_student_delete_log
AFTER DELETE ON students
FOR EACH ROW
EXECUTE FUNCTION log_deleted_student();


CREATE TABLE teacher_log_table (
    log_id SERIAL PRIMARY KEY,
    teacher_id INT,
    old_name VARCHAR(100),
    new_name VARCHAR(100),
    old_email VARCHAR(100),
    new_email VARCHAR(100),
    old_phone VARCHAR(20),
    new_phone VARCHAR(20),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE OR REPLACE FUNCTION log_teacher_update()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO teacher_log_table (
        teacher_id,
        old_name,
        new_name,
        old_email,
        new_email,
        old_phone,
        new_phone,
        changed_at
    )
    VALUES (
        OLD.teacher_id,
        OLD.name,
        NEW.name,
        OLD.email,
        NEW.email,
        OLD.phone,
        NEW.phone,
        CURRENT_TIMESTAMP
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_teacher_update_log
AFTER UPDATE ON teachers
FOR EACH ROW
EXECUTE FUNCTION log_teacher_update();

