import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
import handlers
import admin


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_routers(admin.router, handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
