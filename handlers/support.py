from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from handlers.start import authorized_users
from states.support_question import SupportQuestion
from utils.logger import log_info
from keyboards.support import support_inline_menu


router = Router()

ADMIN_CHAT_ID = 7288278555  # <-- сюда свой Telegram ID

# Храним все тикеты тут: user_id -> {username, question}
tickets = {}

# Главное меню поддержки
def support_inline_menu(is_admin=False):
    buttons = [
        [types.InlineKeyboardButton(text="📩 Связь с менеджером", callback_data="contact_manager")]
    ]

    if is_admin:
        buttons.append([types.InlineKeyboardButton(text="📄 Список тикетов", callback_data="list_tickets")])

    buttons.append([types.InlineKeyboardButton(text="❓ Часто задаваемые вопросы", callback_data="show_faq")])
    buttons.append([types.InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура выбора ученика
def choose_student_inline_keyboard_support(students):
    buttons = [
        [types.InlineKeyboardButton(text=student[1], callback_data=f"select_support_student:{student[0]}")]
        for student in students
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Начало работы в разделе поддержкиа
@router.message(F.text == "Поддержка")
async def support_start(message: types.Message, state: FSMContext):
    user_data = authorized_users.get(message.from_user.id)
    if not user_data:
        await message.answer("⚠️ Сначала пройдите авторизацию через /start.")
        return

    students = user_data.get("students", [])
    await state.update_data(current_action="support")

    if len(students) == 1:
        await state.update_data(selected_student_id=students[0][0])
        await message.answer("💬 Выберите действие:", reply_markup=support_inline_menu())
    else:
        await message.answer("👤 Выберите ученика для поддержки:", reply_markup=choose_student_inline_keyboard_support(students))
        await state.set_state(SupportQuestion.choosing_student_for_support)

# Выбор ученика для поддержки
@router.callback_query(F.data.startswith("select_support_student:"))
async def choose_student_support(callback: types.CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split(":")[1])

    await state.update_data(selected_student_id=student_id)
    await callback.message.edit_text("💬 Выберите действие:", reply_markup=support_inline_menu())
    await state.clear()
    await callback.answer()

# Кнопка "Связь с менеджером"
@router.callback_query(F.data == "contact_manager")
async def start_support_question(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Пожалуйста, опишите ваш вопрос. Менеджер получит сообщение и ответит вам.")
    await state.set_state(SupportQuestion.writing_question)
    await callback.answer()

# Получение текста вопроса от пользователя
@router.message(SupportQuestion.writing_question)
async def receive_support_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id", None)

    tickets[message.from_user.id] = {
        "username": message.from_user.username or f"id{message.from_user.id}",
        "question": message.text.strip()
    }

    text_to_admin = f"📩 Новый вопрос от пользователя @{tickets[message.from_user.id]['username']}\n\n"
    if student_id:
        text_to_admin += f"👤 Ученик ID: {student_id}\n"
    text_to_admin += f"❓ Вопрос:\n{tickets[message.from_user.id]['question']}"

    await message.bot.send_message(ADMIN_CHAT_ID, text_to_admin)
    log_info(f"Вопрос от пользователя {message.from_user.id}: {tickets[message.from_user.id]['question']}")

    await message.answer("✅ Ваш вопрос отправлен менеджеру! Ожидайте ответа.")
    await state.clear()

# Показать список тикетов
@router.callback_query(F.data == "list_tickets")
async def show_ticket_list(callback: types.CallbackQuery, state: FSMContext):
    if not tickets:
        await callback.message.answer("❗ Нет активных тикетов.")
        await callback.answer()
        return

    keyboard = []
    for user_id, info in tickets.items():
        keyboard.append([
            types.InlineKeyboardButton(
                text=f"{info['username']}: {info['question'][:20]}...",
                callback_data=f"open_ticket:{user_id}"
            )
        ])

    await callback.message.answer("📄 Активные тикеты:", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

# Открыть тикет для ответа
@router.callback_query(F.data.startswith("open_ticket:"))
async def open_ticket(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    await state.update_data(current_ticket_user_id=user_id)
    await callback.message.answer(f"✉️ Теперь отправьте сообщение для пользователя @{tickets[user_id]['username']}.")
    await state.set_state(SupportQuestion.answering_ticket)
    await callback.answer()

# Ответ менеджера пользователю
@router.message(SupportQuestion.answering_ticket)
async def send_answer_to_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("current_ticket_user_id")

    try:
        await message.bot.send_message(user_id, f"📩 Ответ от менеджера:\n\n{message.text}")
        await message.answer("✅ Ответ отправлен пользователю!")
    except Exception as e:
        await message.answer(f"⚠️ Не удалось отправить сообщение пользователю.\nОшибка: {e}")

    await state.clear()

# Кнопка "Часто задаваемые вопросы"
@router.callback_query(F.data == "show_faq")
async def show_faq(callback: types.CallbackQuery):
    text = """
❓ Часто задаваемые вопросы:

1. Как изменить расписание?
— Свяжитесь с менеджером через раздел поддержки.

2. Как настроить напоминания об уроках?
— Раздел "Настройка уведомлений" в главном меню.

3. Как узнать прогресс ребёнка?
— Раздел "Прогресс ученика".

(Этот список можно дополнять)
"""
    await callback.message.answer(text)
    await callback.answer()

# Назад в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("🏠 Вы вернулись в главное меню.")
    await callback.answer()
