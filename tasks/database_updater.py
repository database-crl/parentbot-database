import asyncio
from database.db import download_csv_files_from_github, create_database_from_csv, get_connection
import sqlite3

async def auto_update_database(database_path: str, github_csv_base_url: str):
    while True:
        try:
            print("🔄 Автообновление базы данных началось...")
            # Скачиваем свежие CSV
            download_csv_files_from_github(github_csv_base_url, "db")
            # Пересобираем базу
            create_database_from_csv("db", database_path)

            # Переподключаемся к новой базе
            conn = sqlite3.connect(database_path)
            globals()["conn"] = conn  # заменяем глобальное соединение в db.py

            print("✅ База данных успешно обновлена!")
        except Exception as e:
            print(f"❌ Ошибка автообновления базы данных: {e}")

        # Спим сутки (86400 секунд)
        await asyncio.sleep(86400)
