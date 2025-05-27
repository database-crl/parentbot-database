import sqlite3
import os
import requests
import csv

conn = None

def download_csv_files_from_github(base_url: str, save_folder: str):
    files = [
        "parents.csv",
        "students.csv",
        "schedule.csv",
        "logs.csv",
        "notifications_settings.csv"
    ]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for file in files:
        url = f"{base_url}/{file}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(save_folder, file), 'wb') as f:
                f.write(response.content)
            print(f"✅ Скачан {file}")
        else:
            raise Exception(f"❌ Не удалось скачать {file} (Статус: {response.status_code})")

def create_database_from_csv(folder_path: str, db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS parents")
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS schedule")
    cursor.execute("DROP TABLE IF EXISTS logs")
    cursor.execute("DROP TABLE IF EXISTS notifications_settings")

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
        time TEXT,
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

    def insert_from_csv(csv_file, table_name, columns):
        with open(os.path.join(folder_path, csv_file), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            to_db = [tuple(row[col] for col in columns) for row in reader]

        placeholders = ','.join('?' * len(columns))
        cursor.executemany(f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})", to_db)
    cursor.execute("DELETE FROM schedule")
    
    insert_from_csv('parents.csv', 'parents', ['id', 'parent_id', 'parent_name'])
    insert_from_csv('students.csv', 'students', ['id', 'student_name', 'parent_id'])
    insert_from_csv('schedule.csv', 'schedule', ['id', 'student_id', 'date', 'topic'])
    insert_from_csv('logs.csv', 'logs', ['id', 'user_id', 'action', 'timestamp', 'details'])
    insert_from_csv('notifications_settings.csv', 'notifications_settings', ['id', 'user_id', 'student_id', 'schedule_changes', 'reminder_2h', 'homework_ready'])

    conn.commit()
    conn.close()
    print(f"✅ База данных {db_path} успешно собрана из CSV файлов.")

def create_connection(database_path: str, github_csv_base_url: str = None):
    global conn

    if github_csv_base_url:
        print("📥 Скачиваю CSV-файлы с GitHub...")
        download_csv_files_from_github(github_csv_base_url, "db")
        print("🛠 Собираю базу данных из CSV...")
        create_database_from_csv("db", database_path)

    conn = sqlite3.connect(database_path)


def get_connection():
    global conn
    if conn is None:
        raise Exception("База данных не подключена! Сначала вызови create_connection().")
    return conn
