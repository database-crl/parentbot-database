from aiogram import BaseMiddleware
from aiogram.types import Update
from utils.logger import log_error
import traceback

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            error_text = f"Ошибка: {str(e)}\n{traceback.format_exc()}"
            log_error(error_text)
            # При желании можно отправить сообщение админу здесь
            return
