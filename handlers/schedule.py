from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from handlers.start import authorized_users
from states.student_selection import StudentSelection
from database.models import get_schedule_for_student
from datetime import datetime

router = Router()

# Функция для меню расписания
def schedule_inline_menu():
    buttons = [
        [types.InlineKeyboardButton(text="🔜 Ближайшие занятия", callback_data="upcoming_lessons")],
        [types.InlineKeyboardButton(text="⏮ Прошедшие уроки", callback_data="past_lessons")],
        [types.InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Функция выбора ученика
def choose_student_inline_keyboard(students):
    buttons = [[types.InlineKeyboardButton(text=student[1], callback_data=f"select_student:{student[0]}")] for student in students]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Нажатие на кнопку "Расписание"
@router.message(F.text == "Расписание")
async def handle_schedule(message: types.Message, state: FSMContext):
    user_data = authorized_users.get(message.from_user.id)
    if not user_data:
        await message.answer("⚠️ Пожалуйста, авторизуйтесь через /start.")
        return

    students = user_data.get("students", [])
    await state.update_data(current_action="schedule")

    if len(students) == 1:
        await state.update_data(selected_student_id=students[0][0])
        await message.answer(f"📚 Выбран ученик: {students[0][1]}", reply_markup=schedule_inline_menu())
    else:
        await message.answer("👤 Выберите ученика:", reply_markup=choose_student_inline_keyboard(students))
        await state.set_state(StudentSelection.choosing_student_for_schedule)

# Выбор ученика через Inline-кнопку
@router.callback_query(F.data.startswith("select_student:"))
async def select_student_callback(callback: types.CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split(":")[1])

    await state.update_data(selected_student_id=student_id)  # 🧠 сохраняем ученика

    user_data = authorized_users.get(callback.from_user.id)
    students = user_data.get("students", [])
    student_name = next((s[1] for s in students if s[0] == student_id), "Ученик")

    await callback.message.edit_text(f"📚 Вы выбрали: {student_name}", reply_markup=schedule_inline_menu())
    await callback.answer()


# Показать ближайшие занятия
@router.callback_query(F.data == "upcoming_lessons")
async def show_upcoming_lessons(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id")

    if not student_id:
        await callback.message.edit_text("❗ Сначала выберите ученика.")
        await callback.answer()
        return

    lessons = get_schedule_for_student(student_id)
    now = datetime.now()

    upcoming = [
        lesson for lesson in lessons
        if lesson[3] and datetime.strptime(f"{lesson[2]} {lesson[3]}", "%Y-%m-%d %H:%M") >= now
    ]

    if not upcoming:
        await callback.message.edit_text("❗ Нет запланированных занятий.")
        await callback.answer()
        return

    text = "🔜 Ближайшие занятия:\n\n"
    for lesson in upcoming:
        lesson_dt = datetime.strptime(f"{lesson[2]} {lesson[3]}", "%Y-%m-%d %H:%M")
        lesson_date = lesson_dt.strftime("%d.%m.%Y %H:%M")
        text += f"📅 {lesson_date} — {lesson[4]}\n"  # lesson[4] = topic

    await callback.message.edit_text(text)
    await callback.answer()

# Показать прошедшие уроки
@router.callback_query(F.data == "past_lessons")
async def show_past_lessons(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id")

    if not student_id:
        await callback.message.answer("❗ Сначала выберите ученика.")
        await callback.answer()
        return

    lessons = get_schedule_for_student(student_id)
    now = datetime.now()

    past = [
        lesson for lesson in lessons
        if lesson[3] and datetime.strptime(f"{lesson[2]} {lesson[3]}", "%Y-%m-%d %H:%M") < now
    ]


    if not past:
        await callback.message.answer("❗ Нет прошедших уроков.")
        await callback.answer()
        return

    text = "⏮ Прошедшие уроки:\n\n"
    for lesson in past[-4:]:
        lesson_dt = datetime.strptime(f"{lesson[2]} {lesson[3]}", "%Y-%m-%d %H:%M")
        lesson_date = lesson_dt.strftime("%d.%m.%Y %H:%M")
        text += f"📅 {lesson_date} — {lesson[4]}\n"  # <= lesson[4] должен быть topic

    await callback.message.answer(text)
    await callback.answer()

# Назад в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.delete()  # Удалить старое сообщение с кнопками
    await callback.message.answer("🏠 Вы вернулись в главное меню.")
    await callback.answer()
