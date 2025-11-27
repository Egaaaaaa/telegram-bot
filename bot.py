import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8523590707:AAF7hd66xppfiBeDveh-nw0lxSQrvWFiyxk"  # вставь свой токен
ADMIN_ID = 8523590707  # твой ID для админ-команд

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# Загружаем данные из файла
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

# ---------------- Команды ----------------

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет, друзья! 👋\n"
        "Я бот для учета доходов, чтобы мы вместе следили за своими накоплениями 💰.\n\n"
        "Команды бота:\n"
        "/add <сумма> — добавить доход\n"
        "/remove <сумма> — снять часть дохода\n"
        "/total — общий доход всех участников\n"
        "/my — твоя история\n"
        "/top — топ участников\n"
        "/reset_user — обнулить свой доход\n"
        "/reset_all — обнулить всех (только админ)\n\n"
        "Желаю вам успешно копить на наши мечты в Радмире 🌟\n"
        "Каждая небольшая сумма приближает нас к цели!"
    )


# /add <сумма>
@dp.message(Command("add"))
async def add_amount(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Используй: /add <сумма>")

    try:
        amount = int(parts[1])
    except ValueError:
        return await message.answer("Сумма должна быть числом.")

    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name

    if user_id not in user_data:
        user_data[user_id] = {"name": username, "total": 0, "history": []}

    user_data[user_id]["total"] += amount
    user_data[user_id]["history"].append(amount)
    save_data()

    total_user = user_data[user_id]["total"]
    total_all = sum(u["total"] for u in user_data.values())

    await message.answer(f"@{username} закинул бабки в общий доход — {amount}₸")
    await message.answer(f"@{username} всего закинул: {total_user}₸\nОбщая сумма всех участников: {total_all}₸")

# /remove <сумма>
@dp.message(Command("remove"))
async def remove_amount(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Используй: /remove <сумма>")

    try:
        amount = int(parts[1])
    except ValueError:
        return await message.answer("Сумма должна быть числом.")

    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name

    if user_id not in user_data:
        return await message.answer("У тебя нет дохода для снятия.")

    if amount > user_data[user_id]["total"]:
        return await message.answer("У тебя нет столько денег.")

    user_data[user_id]["total"] -= amount
    user_data[user_id]["history"].append(-amount)
    save_data()

    await message.answer(f"@{username} снял {amount}₸. Новый итог: {user_data[user_id]['total']}₸")

# /total
@dp.message(Command("total"))
async def total(message: Message):
    if not user_data:
        return await message.answer("Пока никто ничего не добавил.")
    total_all = sum(u["total"] for u in user_data.values())
    await message.answer(f"Общий доход всех участников: {total_all}₸")

# /my
@dp.message(Command("my"))
async def my_history(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        return await message.answer("Ты пока ничего не добавлял.")
    history = "\n".join([f"{i+1}. {x}₸" for i, x in enumerate(user_data[user_id]["history"])])
    total_user = user_data[user_id]["total"]
    await message.answer(f"Твой итог: {total_user}₸\nИстория:\n{history}")

# /top
@dp.message(Command("top"))
async def top_users(message: Message):
    if not user_data:
        return await message.answer("Пока нет участников.")
    sorted_users = sorted(user_data.values(), key=lambda x: x["total"], reverse=True)
    text = "🏆 Топ участников:\n"
    for i, u in enumerate(sorted_users[:10]):
        text += f"{i+1}. @{u['name']} — {u['total']}₸\n"
    await message.answer(text)

# /reset_user
@dp.message(Command("reset_user"))
async def reset_user(message: Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name
    if user_id in user_data:
        user_data[user_id]["total"] = 0
        user_data[user_id]["history"] = []
        save_data()
        await message.answer(f"@{username} твой доход обнулен!")
    else:
        await message.answer("У тебя нет дохода для обнуления.")

# /reset_all
@dp.message(Command("reset_all"))
async def reset_all(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("У тебя нет прав для этой команды.")
    global user_data
    user_data = {}
    save_data()
    await message.answer("Все доходы участников обнулены!")

# ---------------- Запуск ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
