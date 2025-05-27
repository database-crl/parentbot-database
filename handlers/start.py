from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from database.models import get_parent_by_id, get_students_by_parent
from keyboards.menu import main_menu
from keyboards.support import support_inline_menu
from utils.logger import log_info
from config import ADMIN_CHAT_ID
import os
import subprocess
import csv
import subprocess
from datetime import datetime

router = Router()

# Словарь для хранения авторизованных пользователей
authorized_users = {}


# Функция логирования в logs.csv
def log_action(user_id: int, action: str, details: str = ""):
    log_path = "db/logs.csv"
    already_logged = False

    # Проверка: уже существует такой лог?
    if os.path.exists(log_path):
        with open(log_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["user_id"] == str(user_id) and row["action"] == action:
                    already_logged = True
                    break

    if already_logged:
        print(f"⏩ Лог уже существует для user_id={user_id}, action={action}")
        return

    # Подсчёт строк для ID
    if os.path.exists(log_path):
        with open(log_path, mode="r", encoding="utf-8") as file:
            total_rows = sum(1 for _ in file) - 1  # без заголовка
    else:
        total_rows = 0

    next_id = total_rows + 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Добавляем запись
    with open(log_path, mode="a", encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        if total_rows == 0:
            writer.writerow(["id", "user_id", "action", "timestamp", "details"])
        writer.writerow([next_id, user_id, action, timestamp, details])

    # Git push
    try:
        subprocess.run(["git", "add", log_path], check=True)
        subprocess.run(["git", "commit", "-m", f"auto: лог {action.lower()} — {user_id}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Лог отправлен в GitHub")
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при push в GitHub:", e)

# Автопуш логов в GitHub
def push_logs_to_github():
    try:
        subprocess.run(["git", "add", "db/logs.csv"], check=True)
        subprocess.run(["git", "commit", "-m", "auto: добавлена запись логов"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Логи отправлены в GitHub")
    except Exception as e:
        print("❌ Ошибка при push в GitHub:", e)


# Команда /start
@router.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_CHAT_ID:
        await message.answer("👑 Вы вошли как администратор!", reply_markup=support_inline_menu(is_admin=True))
        await state.clear()
        return

    await message.answer("👋 Привет! Пожалуйста, введите ваш ID родителя из 'Сетевого города'.")
    await state.clear()


# Обработка ID родителя
@router.message(lambda message: message.text.isdigit())
async def handle_parent_id(message: types.Message):
    if message.from_user.id == ADMIN_CHAT_ID:
        return  # Админ не проходит авторизацию

    user_input = message.text.strip()

    # Уже авторизован
    if authorized_users.get(message.from_user.id):
        await message.answer("✅ Вы уже вошли в систему. Пожалуйста, используйте меню ниже.", reply_markup=main_menu())
        return

    # Проверка в БД
    parent = get_parent_by_id(user_input)
    if not parent:
        await message.answer("⚠️ Ваш ID не найден в базе данных. Пожалуйста, свяжитесь с менеджером.")
        log_info(f"User {message.from_user.id} ввёл несуществующий ID: {user_input}")
        log_action(message.from_user.id, "Попытка авторизации — ID не найден", f"Введённый ID: {user_input}")
        push_logs_to_github()
        return

    students = get_students_by_parent(user_input)
    authorized_users[message.from_user.id] = {
        "parent_id": user_input,
        "parent_name": parent[2],
        "students": students
    }

    # Приветствие
    if len(students) == 1:
        welcome_text = f"✅ Добро пожаловать, {parent[2]}!\nВы перешли в главное меню."
    else:
        welcome_text = f"✅ Добро пожаловать, {parent[2]}!\nВаши ученики:\n\n"
        for student in students:
            welcome_text += f"👤 {student[1]}\n"
        welcome_text += "\nВы перешли в главное меню."

    await message.answer(welcome_text, reply_markup=main_menu())

    log_action(
        user_id=message.from_user.id,
        action="Успешная авторизация",
        details=f"ФИО родителя: {parent[2]}"
    )
