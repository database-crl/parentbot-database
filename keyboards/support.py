from aiogram import types

def support_inline_menu(is_admin=False):
    buttons = [
        [types.InlineKeyboardButton(text="📩 Связь с менеджером", callback_data="contact_manager")]
    ]

    if is_admin:
        buttons.append([types.InlineKeyboardButton(text="📄 Список тикетов", callback_data="list_tickets")])

    buttons.append([types.InlineKeyboardButton(text="❓ Часто задаваемые вопросы", callback_data="show_faq")])
    buttons.append([types.InlineKeyboardButton(text="⬅ Назад", callback_data="back_to_menu")])

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
