# 🏫 School Database Management System (PostgreSQL)

A complete School Database Management System built using PostgreSQL.  
This project demonstrates practical database concepts including:

- Relational schema design
- Foreign key relationships
- Views
- Triggers
- Audit logging
- User roles & permissions
- Sample data generation

---

# 📌 Features

- Fully normalized relational database
- Bulk sample data insertion
- Multiple SQL views
- Audit & activity logging using triggers
- Role-based access control (RBAC)
- Teacher/Class/Subject mapping
- Fee management system
- Student contact management

---

# 🧱 Database Schema

## Main Tables

| Table | Description |
|------|-------------|
| `teachers` | Stores teacher information |
| `classes` | Stores class details |
| `students` | Stores student records |
| `subjects` | Stores subjects |
| `teacher_class_subject` | Teacher-Class-Subject mapping |
| `fees` | Student fee records |
| `contact_info` | Student guardian/contact details |

---

# 📋 Audit & Log Tables

| Table | Purpose |
|------|---------|
| `deleted_student_log` | Tracks deleted students |
| `teacher_log_table` | Tracks teacher updates |
| `student_log_table` | Tracks student updates |
| `teacher_delete_log` | Tracks deleted teachers |
| `teacher_insert_log` | Tracks inserted teachers |
| `student_insert_log` | Tracks inserted students |

---

# 🔗 Relationships

- One class → many students
- One teacher → class incharge
- Many-to-many:
  - teachers
  - classes
  - subjects
- One student → many fee records
- One student → many contacts

---

# 📊 Views

The project includes the following SQL views:

| View | Purpose |
|------|---------|
| `student_contact_details` | Student + guardian details |
| `student_complete_details` | Complete student information |
| `class_subject_teacher` | Teacher-Class-Subject mapping |
| `student_fee_details` | Student fee records |
| `class_overview` | Total students per class |

---

# 🔄 Triggers & Audit System

## Student Triggers

| Trigger | Action |
|---------|--------|
| `trg_student_delete_log` | Logs deleted students |
| `trg_student_update_log` | Logs updated students |
| `trg_student_insert_log` | Logs inserted students |

---

## Teacher Triggers

| Trigger | Action |
|---------|--------|
| `trg_teacher_update_log` | Logs teacher updates |
| `trg_teacher_delete_log` | Logs deleted teachers |
| `trg_teacher_insert_log` | Logs inserted teachers |

---

# 👥 Database Users & Permissions

## Users

| User | Access Level |
|------|--------------|
| `yousuf` | Full access on main tables |
| `talha` | SELECT, INSERT, UPDATE |
| `umar` | Read-only access |

---

## Permission Details

### `yousuf`
- Full administrative access

### `talha`
- Can:
  - SELECT
  - INSERT
  - UPDATE
- Cannot DELETE data

### `umar`
- Read-only access
- Can view logs & views

---

# 🧪 Sample Data

The database includes generated sample data:

- 10 teachers
- 5 classes (Grade 1–5)
- 6 subjects
- 250 students
- Fee records for all students
- Contact information for all students

---

# 🛠️ Technologies Used

- PostgreSQL
- SQL
- PL/pgSQL

---

# 📚 SQL Concepts Covered

- DDL (CREATE, ALTER)
- DML (INSERT, UPDATE, DELETE)
- DCL (GRANT, REVOKE)
- Views
- Triggers
- Functions
- Foreign Keys
- Constraints
- Aggregate Functions
- Audit Logging
- Role-based Access Control

---

# 🚀 Setup Instructions

## 1. Create Database

```sql
CREATE DATABASE school;
```

---

## 2. Connect to Database

```sql
\c school
```

---

## 3. Run SQL Script

Execute the SQL file containing:

1. Table creation
2. Data insertion
3. Views
4. Trigger functions
5. Triggers
6. Users & privileges

---

# 🔐 Security Features

- Restricted database access
- Table-level privileges
- Sequence permissions
- Audit tracking using triggers
- User activity logging using `CURRENT_USER`

---

# 👨‍💻 Authors

- Muhammad Yousuf
- Talha Shahzad
- Muhammad Umar
---

# ⭐ Notes

This project is designed for:

- Learning PostgreSQL
- Academic database projects
- Understanding real-world database systems
- Practicing SQL concepts

---
