from aiogram.fsm.state import State, StatesGroup

class SupportQuestion(StatesGroup):
    choosing_student_for_support = State()
    writing_question = State()
    answering_ticket = State()  # <-- Добавляем это состояние для ответа менеджера
