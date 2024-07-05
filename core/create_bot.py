from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from Framework.MiddleWare import ThrottlingMiddleware
from bot_config import TOKEN

storage = MemoryStorage()
bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(storage=storage)
dp.message.middleware.register(ThrottlingMiddleware(rate=2))
