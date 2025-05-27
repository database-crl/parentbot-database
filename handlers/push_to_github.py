import subprocess
import datetime
import os

def run(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Ошибка: {result.stderr.strip()}")
    return result.stdout.strip()

def push_logs_to_github():
    os.chdir(os.path.dirname(__file__))  # переходим в папку со скриптом

    # Проверка, есть ли изменения в logs.csv
    diff = run("git status --porcelain db/logs.csv")
    if not diff:
        print("ℹ️ logs.csv не изменён. Коммит не нужен.")
        return

    # Формируем дату в строку
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    print("📤 Обнаружены изменения. Добавляем в коммит...")
    run("git add db/logs.csv")
    run(f'git commit -m "auto: лог авторизации от {date_str}"')

    print("🔄 Подтягиваем изменения с GitHub...")
    run("git pull --rebase origin main")

    print("🚀 Пушим в GitHub...")
    run("git push")

    print("✅ Готово!")

if __name__ == "__main__":
    push_logs_to_github()
