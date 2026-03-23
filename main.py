import asyncio
import logging
import sys
from os import getenv
from string import ascii_lowercase, ascii_uppercase, digits, punctuation
from random import choice
from dotenv import load_dotenv
from Models import DBManager
from html import escape

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram import F
from aiogram.types import FSInputFile, URLInputFile
load_dotenv()
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()
dbm = DBManager()

keys = [
    "Длинна пароля",
    "Заглавные буквы",
    "Строчные буквы",
    "Цифры",
    "Специальные символы"
]
columns = ["len", "upper", "lower", "digits", "special"]
keys_to_columns = dict(zip(keys, columns))
types = {keys[i]: int if i == 0 else bool for i in range(0, len(keys))}

back_button = InlineKeyboardButton(text="Назад", callback_data="menu")

def menu(message: Message, f: bool = True):
    dbm.confirm_user(message.from_user.id)
    button1 = InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generation")
    button2 = InlineKeyboardButton(text="История генераций", callback_data="history")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    return message.answer("Добро пожаловать в генератор паролей!", reply_markup=keyboard)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await menu(message)

@dp.callback_query(F.data == "menu")
async def menu_handler(callback: CallbackQuery):
    dbm.confirm_user(callback.message.from_user.id)
    button1 = InlineKeyboardButton(text="Сгенерировать пароль", callback_data="generation")
    button2 = InlineKeyboardButton(text="История генераций", callback_data="history")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    await callback.message.edit_text("Добро пожаловать в генератор паролей!", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "history")
async def handle_history_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    ish = dbm.is_saving_history(user_id)
    txt = "не " if ish else ""
    button3 = InlineKeyboardButton(text=(txt + "сохранять историю поиска").capitalize(), callback_data="save_history")
    button4 = InlineKeyboardButton(text="Очистить историю", callback_data="clear_history")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button3, button4], [back_button]])
    history = dbm.get_history(user_id)
    if len(history) == 0:
        ans = "У вас нету сохранённых паролей"
    else:
        ans = "\n".join(history)
    ans = escape(ans)
    await callback.message.edit_text(ans, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "save_history")
async def not_to_save_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    ish = dbm.is_saving_history(user_id)
    dbm.save_history(user_id, not ish)
    button1 = InlineKeyboardButton(text="Назад", callback_data="history")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
    await callback.message.edit_text(f"Успешно! История генераций {'не ' if ish else ''}сохраняется.", reply_markup=keyboard)

@dp.callback_query(F.data == "clear_history")
async def clear_history_button(callback: CallbackQuery):
    user_id = callback.from_user.id
    dbm.clear_history(user_id)
    button1 = InlineKeyboardButton(text="Назад", callback_data="history")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
    await callback.message.edit_text("История очищена!", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data == "generation")
async def generation_menu(callback: CallbackQuery):
    out = ["**Выберите параметры пароля**"]
    user_id = callback.from_user.id
    val = dbm.get_password_settings(user_id)
    for key, val in zip(keys, val):
        if types[key] is int: out.append(f"{key}: {val}")
        else: out.append(f"{key}: {'✅' if val else '❌'}")
    # out.append(str(dbm.get_password_settings(callback.from_user.id)))
    button1 = InlineKeyboardButton(text="-5", callback_data="-5")
    button2 = InlineKeyboardButton(text="-1", callback_data="-1")
    button3 = InlineKeyboardButton(text="+1", callback_data="+1")
    button4 = InlineKeyboardButton(text="+5", callback_data="+5")
    button5 = InlineKeyboardButton(text="Заглавные", callback_data="u")
    button6 = InlineKeyboardButton(text="Строчные", callback_data="l")
    button7 = InlineKeyboardButton(text="Цифры", callback_data="d")
    button8 = InlineKeyboardButton(text="Спецсимволы", callback_data="s")
    button9 = InlineKeyboardButton(text="Сгенерировать", callback_data="gen")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2, button3, button4], [button5, button6, button7, button8], [button9, back_button]])
    await callback.message.edit_text("\n".join(out), reply_markup=keyboard)
    await callback.answer()

def change_password_settings(user_id: int, val: str, delta: int = 0):
    index = columns.index(val)
    tp = types[keys[index]]
    cur = int(dbm.get_password_settings(user_id)[index])
    if tp is bool:
        dbm.change_password_parameter(user_id, val, int(not cur))
    else:
        if not 1 <= cur + delta <= 200: return False
        dbm.change_password_parameter(user_id, val, cur + delta)
    return True

@dp.callback_query(F.data == "-5")
async def pwd_ln_m5(callback: CallbackQuery):
    status = change_password_settings(callback.from_user.id, "len", -5)
    if status:
        await generation_menu(callback)
    else:
        button1 = InlineKeyboardButton(text="Назад", callback_data="generation")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
        await callback.message.edit_text("Недопустимая длинна пароля", reply_markup=keyboard)
        await callback.answer()

@dp.callback_query(F.data == "-1")
async def pwd_ln_m5(callback: CallbackQuery):
    status = change_password_settings(callback.from_user.id, "len", -1)
    if status:
        await generation_menu(callback)
    else:
        button1 = InlineKeyboardButton(text="Назад", callback_data="generation")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
        await callback.message.edit_text("Недопустимая длинна пароля", reply_markup=keyboard)
        await callback.answer()

@dp.callback_query(F.data == "+1")
async def pwd_ln_m5(callback: CallbackQuery):
    status = change_password_settings(callback.from_user.id, "len", 1)
    if status:
        await generation_menu(callback)
    else:
        button1 = InlineKeyboardButton(text="Назад", callback_data="generation")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
        await callback.message.edit_text("Недопустимая длинна пароля", reply_markup=keyboard)
        await callback.answer()

@dp.callback_query(F.data == "+5")
async def pwd_ln_m5(callback: CallbackQuery):
    status = change_password_settings(callback.from_user.id, "len", 5)
    if status:
        await generation_menu(callback)
    else:
        button1 = InlineKeyboardButton(text="Назад", callback_data="generation")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1]])
        await callback.message.edit_text("Недопустимая длинна пароля", reply_markup=keyboard)
        await callback.answer()

@dp.callback_query(F.data == "u")
async def upper(callback: CallbackQuery):
    change_password_settings(callback.from_user.id, "upper")
    await generation_menu(callback)

@dp.callback_query(F.data == "l")
async def upper(callback: CallbackQuery):
    change_password_settings(callback.from_user.id, "lower")
    await generation_menu(callback)

@dp.callback_query(F.data == "d")
async def upper(callback: CallbackQuery):
    change_password_settings(callback.from_user.id, "digits")
    await generation_menu(callback)

@dp.callback_query(F.data == "s")
async def upper(callback: CallbackQuery):
    change_password_settings(callback.from_user.id, "special")
    await generation_menu(callback)

@dp.callback_query(F.data == "gen")
async def gen(callback: CallbackQuery):
    user_id = callback.from_user.id
    ln, upper, lower, dgts, special = dbm.get_password_settings(user_id)
    if not 1 <= ln <= 200:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
        await callback.message.edit_text("Недопустимая длинна пароля", reply_markup=keyboard)
        await callback.answer()
    else:
        abc = ""
        if upper: abc += ascii_uppercase
        if lower: abc += ascii_lowercase
        if dgts: abc += digits
        if special: abc += punctuation
        if len(abc) == 0:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
            await callback.message.edit_text("Выберите символы, из которых будет состоять пароль", reply_markup=keyboard)
            await callback.answer()
        else:
            password = ""
            for i in range(0, ln):
                password += choice(abc)
            if dbm.is_saving_history(user_id):
                dbm.add_to_history(user_id, password)
            button1 = InlineKeyboardButton(text="История", callback_data="history")
            button2 = InlineKeyboardButton(text="Заново", callback_data="gen")
            button3 = InlineKeyboardButton(text="Назад", callback_data="generation")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2], [button3]])
            await callback.message.edit_text(escape("Сгенерированный пароль:\n" + password), reply_markup=keyboard)

@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("Пожалуйста, воспользуйтесь кнопками под сообщением бота")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
