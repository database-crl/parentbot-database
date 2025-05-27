import asyncio
import os
import time

async def auto_clean_logs(logs_folder: str = "logs", days_to_keep: int = 7):
    while True:
        try:
            print("🧹 Проверяю старые логи для удаления...")

            if not os.path.exists(logs_folder):
                print(f"❗ Папка {logs_folder} не найдена.")
            else:
                now = time.time()
                cutoff = now - (days_to_keep * 86400)  # 86400 секунд = 1 день

                for filename in os.listdir(logs_folder):
                    filepath = os.path.join(logs_folder, filename)
                    if os.path.isfile(filepath):
                        file_mtime = os.path.getmtime(filepath)
                        if file_mtime < cutoff:
                            os.remove(filepath)
                            print(f"🗑 Удалён старый лог: {filename}")

            print("✅ Проверка логов завершена.")
        except Exception as e:
            print(f"❌ Ошибка очистки логов: {e}")

        await asyncio.sleep(86400)  # Проверка каждый день
