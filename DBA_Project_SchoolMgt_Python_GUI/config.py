# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "school_secret_key_2024")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

# Role-based database users
DB_USERS = {
    "yousuf":   {"password": "yousuf",   "role": "admin"},
    "talha":    {"password": "talha",    "role": "editor"},
    "umar":     {"password": "umar",     "role": "viewer"},
    "postgres": {"password": "root", "role": "superuser"},
}

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "school"

# Role permissions
ROLE_PERMISSIONS = {
    "superuser": ["read", "write", "update", "delete", "logs"],
    "admin":     ["read", "write", "update", "delete"],
    "editor":    ["read", "write", "update"],
    "viewer":    ["read"],
}