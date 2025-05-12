import sqlite3
import csv
import os

# Путь к папке с CSV
DB_FOLDER = 'db'

# Название файла SQLite
DB_FILE = 'database.sqlite3'

# Создание подключения к базе
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Удаление таблиц на всякий случай перед созданием (если перегенерируем)
cursor.execute("DROP TABLE IF EXISTS parents")
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute("DROP TABLE IF EXISTS schedule")
cursor.execute("DROP TABLE IF EXISTS logs")
cursor.execute("DROP TABLE IF EXISTS notifications_settings")

# Создание таблиц
cursor.execute("""
CREATE TABLE parents (
    id INTEGER PRIMARY KEY,
    parent_id TEXT,
    parent_name TEXT
)
""")

cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_name TEXT,
    parent_id TEXT
)
""")

cursor.execute("""
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY,
    student_id INTEGER,
    date TEXT,
    topic TEXT
)
""")

cursor.execute("""
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    timestamp TEXT,
    details TEXT
)
""")

cursor.execute("""
CREATE TABLE notifications_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    student_id INTEGER,
    schedule_changes BOOLEAN,
    reminder_2h BOOLEAN,
    homework_ready BOOLEAN
)
""")

# Вставка данных из CSV
def insert_from_csv(csv_file, table_name, columns):
    with open(os.path.join(DB_FOLDER, csv_file), 'r', encoding='utf-8') as file:
        dr = csv.DictReader(file)
        to_db = [tuple(row[col] for col in columns) for row in dr]

    placeholders = ','.join('?' * len(columns))
    cursor.executemany(f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})", to_db)

# Загрузка всех таблиц
insert_from_csv('parents.csv', 'parents', ['id', 'parent_id', 'parent_name'])
insert_from_csv('students.csv', 'students', ['id', 'student_name', 'parent_id'])
insert_from_csv('schedule.csv', 'schedule', ['id', 'student_id', 'date', 'topic'])
insert_from_csv('logs.csv', 'logs', ['id', 'user_id', 'action', 'timestamp', 'details'])
insert_from_csv('notifications_settings.csv', 'notifications_settings', ['id', 'user_id', 'student_id', 'schedule_changes', 'reminder_2h', 'homework_ready'])

# Сохраняем и закрываем соединение
conn.commit()
conn.close()

print(f"✅ База данных '{DB_FILE}' успешно создана из папки '{DB_FOLDER}'!")
