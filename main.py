import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import load_config
from database.db import create_connection
from handlers import start, schedule, progress, notifications, support, exit
from middlewares.error_handler import ErrorHandlerMiddleware
from tasks.database_updater import auto_update_database
from tasks.logs_cleaner import auto_clean_logs
from aiogram.client.default import DefaultBotProperties 

async def main():
    config = load_config()

    logging.basicConfig(level=logging.INFO)
    bot = Bot(
       token=config.token,
       default=DefaultBotProperties(parse_mode="HTML")
   )
    dp = Dispatcher()

    # Подключение базы данных
    create_connection(
        database_path=config.database_path,
        github_csv_base_url=config.github_database_url
    )

    # Регистрируем Middleware обработки ошибок
    dp.update.middleware(ErrorHandlerMiddleware())

    # Регистрируем все обработчики
    dp.include_router(start.router)
    dp.include_router(schedule.router)
    dp.include_router(progress.router)
    dp.include_router(notifications.router)
    dp.include_router(support.router)
    dp.include_router(exit.router)


    # 🚀 Запуск автообновления базы параллельно
    asyncio.create_task(
        auto_update_database(
            database_path=config.database_path,
            github_csv_base_url=config.github_database_url
        )
    )
    
    # 🚀 Запуск автоочистки логов параллельно
    asyncio.create_task(
        auto_clean_logs(
            logs_folder="logs",  # Путь к папке с логами
            days_to_keep=7       # Сколько дней хранить логи
        )
    )

    # Старт бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
