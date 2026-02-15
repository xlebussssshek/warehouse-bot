import asyncio
from aiogram import Bot, Dispatcher
from core.config import BOT_TOKEN
from core.database import init_db
from bot.handlers import router
from logger.logger import logger


async def main():
    await init_db()

    bot= Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info('Бот запущен', extra={"user_id":0, "command": "system", "text":"startup"})

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())