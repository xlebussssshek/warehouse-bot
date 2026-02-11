import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import router
from logger import logger


async def main():
    init_db()

    bot= Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info('Бот запущен', extra={"user_id":0, "command": "system", "text":"startup"})

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())