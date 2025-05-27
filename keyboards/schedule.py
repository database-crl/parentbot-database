from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def schedule_menu():
    keyboard = [
        [KeyboardButton(text="🔜 Ближайшие занятия")],
        [KeyboardButton(text="⏮ Прошедшие уроки")],
        [KeyboardButton(text="➡ Выбрать другого ученика"), KeyboardButton(text="↩ Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def choose_student_keyboard(students):
    buttons = [[KeyboardButton(text=student[1])] for student in students]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
