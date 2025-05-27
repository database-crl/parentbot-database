from aiogram.fsm.state import State, StatesGroup

class StudentSelection(StatesGroup):
    choosing_student_for_schedule = State()       # Выбор ученика для расписания
    choosing_student_for_progress = State()        # Выбор ученика для прогресса
    choosing_student_for_notifications = State()   # Выбор ученика для настроек уведомлений
    choosing_student_for_support = State()         # Выбор ученика для поддержки
