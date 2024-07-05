import asyncio
import logging
from aiogram import Router
from administration.Configs import settings
from ports.db import create_table, sql_start
from core.create_bot import bot
from core.heandlers import dp
router = Router()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    sql_start()
    create_table()
    await settings.check_settings()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=["message", "inline_query", "chat_member", "callback_query", "update_id", "my_chat_member", "pre_checkout_query"])


if __name__ == '__main__':
    asyncio.run(main())
