import subprocess

def push_logs_to_github():
    try:
        subprocess.run(["git", "add", "db/logs.csv"], check=True)
        subprocess.run(["git", "commit", "-m", "auto: обновлён logs.csv"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Логи отправлены в GitHub")
    except Exception as e:
        print("❌ Ошибка при push:", e)
