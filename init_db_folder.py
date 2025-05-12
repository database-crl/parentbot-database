import os
import csv

DB_FOLDER = 'db'

# Структура файлов и их содержимое
db_files = {
    'parents.csv': [
        ['id', 'parent_id', 'parent_name'],
        ['1', '123456789', 'Иванов Иван Иванович'],
        ['2', '987654321', 'Петрова Мария Сергеевна']
    ],
    'students.csv': [
        ['id', 'student_name', 'parent_id'],
        ['1', 'Иванов Сергей Иванович', '123456789'],
        ['2', 'Петрова Анастасия Сергеевна', '987654321'],
        ['3', 'Петров Петр Сергеевич', '987654321']
    ],
    'schedule.csv': [
        ['id', 'student_id', 'date', 'topic'],
        ['1', '1', '2025-05-18', 'Математика: Деление дробей'],
        ['2', '1', '2025-05-19', 'Русский язык: Сложные предложения'],
        ['3', '2', '2025-05-18', 'Физика: Закон Архимеда'],
        ['4', '3', '2025-05-19', 'История: Киевская Русь']
    ],
    'logs.csv': [
        ['id', 'user_id', 'action', 'timestamp', 'details'],
        ['1', '123456789', 'Успешная авторизация', '2025-05-12 15:00:00', 'ФИО родителя: Иванов Иван Иванович']
    ],
    'notifications_settings.csv': [
        ['id', 'user_id', 'student_id', 'schedule_changes', 'reminder_2h', 'homework_ready'],
        ['1', '123456789', '1', '1', '1', '0'],
        ['2', '987654321', '2', '1', '0', '1']
    ]
}

# Создание папки db, если её нет
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)
    print(f"📁 Папка '{DB_FOLDER}' создана.")

# Создание файлов
for filename, content in db_files.items():
    file_path = os.path.join(DB_FOLDER, filename)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(content)
    print(f"✅ Файл '{filename}' создан.")

print("🎉 Инициализация базы данных завершена. Теперь запусти 'create_database.py'.")
