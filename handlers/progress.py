from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from handlers.start import authorized_users
from states.student_selection import StudentSelection
from database.models import get_schedule_for_student
from datetime import datetime

router = Router()

# Функция для меню прогресса ученика
def progress_inline_menu():
    buttons = [
        [types.InlineKeyboardButton(text="✅ Изученные темы", callback_data="studied_topics")],
        [types.InlineKeyboardButton(text="🔜 Предстоящий материал", callback_data="upcoming_topics")],
        [types.InlineKeyboardButton(text="➡ Выбрать другого ученика", callback_data="choose_another_student_progress")],
        [types.InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Функция выбора ученика
def choose_student_inline_keyboard(students):
    buttons = [[types.InlineKeyboardButton(text=student[1], callback_data=f"select_progress_student:{student[0]}")] for student in students]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Обработчик "Прогресс ученика"
@router.message(F.text == "Прогресс ученика")
async def progress_start(message: types.Message, state: FSMContext):
    user_data = authorized_users.get(message.from_user.id)
    if not user_data:
        await message.answer("⚠️ Сначала пройдите авторизацию через /start.")
        return

    students = user_data.get("students", [])
    await state.update_data(current_action="progress")

    if len(students) == 1:
        await state.update_data(selected_student_id=students[0][0])
        await message.answer(f"📚 Выбран ученик: {students[0][1]}", reply_markup=progress_inline_menu())
    else:
        await message.answer("👤 Выберите ученика:", reply_markup=choose_student_inline_keyboard(students))
        await state.set_state(StudentSelection.choosing_student_for_progress)

# Выбор ученика через Inline-кнопку для прогресса
@router.callback_query(F.data.startswith("select_progress_student:"))
async def choose_student_progress(callback: types.CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split(":")[1])

    await state.update_data(selected_student_id=student_id)

    user_data = authorized_users.get(callback.from_user.id)
    students = user_data.get("students", [])
    student_name = next((s[1] for s in students if s[0] == student_id), "Ученик")

    await callback.message.edit_text(f"📚 Выбран ученик: {student_name}", reply_markup=progress_inline_menu())
    await callback.answer()

# Показать изученные темы
@router.callback_query(F.data == "studied_topics")
async def show_studied_topics(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id")

    if not student_id:
        await callback.message.answer("❗ Сначала выберите ученика.")
        await callback.answer()
        return

    lessons = get_schedule_for_student(student_id)
    today = datetime.now().date()

    studied = [lesson for lesson in lessons if datetime.strptime(lesson[2], "%Y-%m-%d").date() < today]

    if not studied:
        await callback.message.answer("❗ Пока нет изученных тем.")
        await callback.answer()
        return

    text = "✅ Изученные темы:\n\n"
    for lesson in studied:
        text += f"📅 {lesson[2]} — {lesson[4]}\n"

    await callback.message.answer(text)
    await callback.answer()

# Показать предстоящий материал
@router.callback_query(F.data == "upcoming_topics")
async def show_upcoming_topics(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id")

    if not student_id:
        await callback.message.answer("❗ Сначала выберите ученика.")
        await callback.answer()
        return

    lessons = get_schedule_for_student(student_id)
    today = datetime.now().date()

    upcoming = [lesson for lesson in lessons if datetime.strptime(lesson[2], "%Y-%m-%d").date() >= today]

    if not upcoming:
        await callback.message.answer("❗ Пока нет предстоящих тем.")
        await callback.answer()
        return

    text = "🔜 Предстоящий материал:\n\n"
    for lesson in upcoming:
        text += f"📅 {lesson[2]} — {lesson[4]}\n"

    await callback.message.answer(text)
    await callback.answer()

# Выбрать другого ученика
@router.callback_query(F.data == "choose_another_student_progress")
async def choose_another_student_progress(callback: types.CallbackQuery, state: FSMContext):
    user_data = authorized_users.get(callback.from_user.id)

    if not user_data:
        await callback.message.answer("⚠️ Пожалуйста, авторизуйтесь через /start.")
        await callback.answer()
        return

    students = user_data.get("students", [])

    await callback.message.edit_text(
        "👤 Выберите ученика:",
        reply_markup=choose_student_inline_keyboard(students)  # <-- правильная функция
    )

    await state.set_state(StudentSelection.choosing_student_for_progress)
    await callback.answer()


# Назад в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.delete()  # Удалить старое сообщение с кнопками
    await callback.message.answer("🏠 Вы вернулись в главное меню.")
    await callback.answer()
