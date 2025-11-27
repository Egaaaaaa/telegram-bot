from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env (если есть)
load_dotenv()

# Токен из Render Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Ошибка: BOT_TOKEN не задан!")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для хранения баланса пользователей
users_balance = {}

# Команды
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Команды:\n"
        "/add <сумма> — добавить доход\n"
        "/remove <сумма> — снять доход\n"
        "/total — общий доход всех участников\n"
        "/my — твоя история"
    )

@dp.message(Command("add"))
async def cmd_add(message: Message):
    try:
        amount = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("Напиши сумму правильно, например: /add 100")
        return

    user_id = message.from_user.id
    users_balance[user_id] = users_balance.get(user_id, 0) + amount
    await message.reply(f"Добавлено {amount}. Твой баланс: {users_balance[user_id]}")

@dp.message(Command("remove"))
async def cmd_remove(message: Message):
    try:
        amount = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.reply("Напиши сумму правильно, например: /remove 50")
        return

    user_id = message.from_user.id
    if users_balance.get(user_id, 0) < amount:
        await message.reply("Недостаточно средств!")
        return

    users_balance[user_id] -= amount
    await message.reply(f"Списано {amount}. Твой баланс: {users_balance[user_id]}")

@dp.message(Command("total"))
async def cmd_total(message: Message):
    total = sum(users_balance.values())
    await message.reply(f"Общий доход всех участников: {total}")

@dp.message(Command("my"))
async def cmd_my(message: Message):
    user_id = message.from_user.id
    balance = users_balance.get(user_id, 0)
    await message.reply(f"Твой баланс: {balance}")

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
