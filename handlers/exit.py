from aiogram import Router, types, F
from handlers.start import authorized_users
from utils.logger import log_info
from database.models import log_action

router = Router()

@router.message(F.text == "Выход")
async def exit_session(message: types.Message):
    user_id = message.from_user.id

    # Если пользователь был авторизован, убираем его
    if authorized_users.get(user_id):
        parent_info = authorized_users.pop(user_id)
        log_info(f"User {user_id} ({parent_info['parent_name']}) вышел из системы.")
        log_action(user_id, "Выход из системы", f"ФИО родителя: {parent_info['parent_name']}")
        await message.answer("🔚 Вы вышли из системы. Чтобы вернуться, введите /start.")
    else:
        # Если пользователь не был авторизован
        log_info(f"User {user_id} попытался выйти без авторизации.")
        await message.answer("ℹ️ Вы не были авторизованы. Чтобы начать работу, введите /start.")
