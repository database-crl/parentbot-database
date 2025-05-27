from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from handlers.start import authorized_users
from states.notification_settings import NotificationSettings
from database.models import get_notifications_settings, toggle_notification_setting

router = Router()

# Меню настроек уведомлений
def notifications_inline_menu(settings):
    buttons = [
        [types.InlineKeyboardButton(
            text=f"🔄 Изменения в расписании {'✅' if settings['schedule_changes'] else '❌'}",
            callback_data="toggle_schedule_changes"
        )],
        [types.InlineKeyboardButton(
            text=f"⏰ Напоминание за 2 часа {'✅' if settings['reminder_2h'] else '❌'}",
            callback_data="toggle_reminder_2h"
        )],
        [types.InlineKeyboardButton(
            text=f"📝 Готовность домашки {'✅' if settings['homework_ready'] else '❌'}",
            callback_data="toggle_homework_ready"
        )],
        [types.InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Клавиатура выбора ученика для уведомлений
def choose_student_inline_keyboard_notifications(students):
    buttons = [
        [types.InlineKeyboardButton(text=student[1], callback_data=f"select_notifications_student:{student[0]}")]
        for student in students
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

# Начало настройки уведомлений
@router.message(F.text == "Настройка уведомлений")
async def notifications_start(message: types.Message, state: FSMContext):
    user_data = authorized_users.get(message.from_user.id)
    if not user_data:
        await message.answer("⚠️ Сначала пройдите авторизацию через /start.")
        return

    students = user_data.get("students", [])
    await state.update_data(current_action="notifications")

    if len(students) == 1:
        await state.update_data(selected_student_id=students[0][0])
        settings = get_notifications_settings(message.from_user.id, students[0][0])
        await message.answer("🔔 Настройка уведомлений:", reply_markup=notifications_inline_menu(settings))
    else:
        await message.answer(
            "👤 Выберите ученика для настройки:",
            reply_markup=choose_student_inline_keyboard_notifications(students)
        )
        await state.set_state(NotificationSettings.choosing_student_for_notifications)

# Выбор ученика для настройки уведомлений
@router.callback_query(F.data.startswith("select_notifications_student:"))
async def choose_student_notifications(callback: types.CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split(":")[1])
    await state.update_data(selected_student_id=student_id)

    settings = get_notifications_settings(callback.from_user.id, student_id)
    await callback.message.edit_text("🔔 Настройка уведомлений:", reply_markup=notifications_inline_menu(settings))
    await state.set_state(None)  # Только обнуляем состояние, данные оставляем
    await callback.answer()

# Переключение настроек уведомлений
@router.callback_query(F.data.startswith("toggle_"))
async def toggle_notifications(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    student_id = data.get("selected_student_id")

    if not student_id:
        await callback.answer("❗ Сначала выберите ученика.", show_alert=True)
        return

    field_map = {
        "toggle_schedule_changes": "schedule_changes",
        "toggle_reminder_2h": "reminder_2h",
        "toggle_homework_ready": "homework_ready"
    }

    field = field_map.get(callback.data)
    if not field:
        await callback.answer("❗ Неверная команда.", show_alert=True)
        return

    toggle_notification_setting(callback.from_user.id, student_id, field)
    settings = get_notifications_settings(callback.from_user.id, student_id)

    await callback.message.edit_text("🔔 Настройка уведомлений обновлена:", reply_markup=notifications_inline_menu(settings))
    await callback.answer()

# Возврат в главное меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()  # При возврате в главное меню — очищаем всё
    await callback.message.delete()
    await callback.message.answer("🏠 Вы вернулись в главное меню.")
    await callback.answer()
