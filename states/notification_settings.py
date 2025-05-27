from aiogram.fsm.state import State, StatesGroup

class NotificationSettings(StatesGroup):
    choosing_student_for_notifications = State()  # Выбор ученика для настройки уведомлений
