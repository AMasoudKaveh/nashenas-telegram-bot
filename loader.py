# loader.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config

# Single shared Bot and Dispatcher instances used across the project.
bot: Bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())
