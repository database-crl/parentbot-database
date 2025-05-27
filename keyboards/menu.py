from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    keyboard = [
        [KeyboardButton(text="Расписание"), KeyboardButton(text="Прогресс ученика")],
        [KeyboardButton(text="Настройка уведомлений"), KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Выход")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
