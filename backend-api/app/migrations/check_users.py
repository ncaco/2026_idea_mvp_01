"""기존 사용자 확인"""
import sqlite3
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "accountbook.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, username, hashed_password FROM users")
users = cursor.fetchall()

print("현재 사용자 목록:")
for user_id, username, hashed_password in users:
    has_pwd = "있음" if hashed_password and len(hashed_password) > 0 else "없음"
    print(f"  ID: {user_id}, Username: {username}, Password: {has_pwd}")

conn.close()
