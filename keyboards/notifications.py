from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Меню настроек уведомлений
def notifications_menu(settings):
    keyboard = [
        [KeyboardButton(text=f"🔄 Изменения в расписании { '✅' if settings['schedule_changes'] else '❌' }")],
        [KeyboardButton(text=f"⏰ Напоминание за 2 часа { '✅' if settings['reminder_2h'] else '❌' }")],
        [KeyboardButton(text=f"📝 Готовность домашнего задания { '✅' if settings['homework_ready'] else '❌' }")],
        [KeyboardButton(text="⬅ Назад в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Выбор ученика для настройки уведомлений
def choose_student_keyboard_notifications(students):
    buttons = [
        [KeyboardButton(text=student[1])] for student in students
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
