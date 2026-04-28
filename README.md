# 🏫 School Database System (PostgreSQL)

A simple and well-structured **school management database** built using PostgreSQL.  
This project demonstrates core database concepts like relationships, views, triggers, and user permissions.

---

## 📌 Features

- Relational database design
- Foreign key relationships
- Sample data insertion (bulk)
- Simple views for querying
- Materialized views for performance
- Triggers for logging changes
- Role-based access control (RBAC)

---

## 🧱 Database Schema

### Tables

- `students` → student records  
- `teachers` → teacher information  
- `classes` → class details  
- `subjects` → subject list  
- `teacher_class_subject` → mapping table  
- `fees` → fee records  
- `contact_info` → guardian/contact details  

---

## 🔗 Relationships

- One class → many students  
- One teacher → class incharge  
- Teachers ↔ Classes ↔ Subjects (many-to-many via mapping table)  
- One student → many fees  
- One student → many contacts  

---

## 📊 Views

- `student_complete_details`  
- `class_subject_teacher`  
- `student_fee_details`  
- `student_contact_details`  
- `class_overview`  

---

## 🔄 Triggers

### 1. Student Delete Log
Stores deleted student records in `deleted_student_log`

### 2. Teacher Update Log
Tracks updates in `teacher_log_table`

---

## 🔐 Users & Permissions

| User   | Access Level |
|--------|-------------|
| yousuf | Full access |
| talha  | SELECT, INSERT, UPDATE |
| umar   | SELECT only |

Permissions are limited to:
- Database: `school`
- Only project tables (not global)

---

## 🧪 Sample Data

- 10 teachers  
- 5 classes (Grade 1–5)  
- 6 subjects  
- 250 students (50 per class)  

---
