from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Domain.functions import bot_in_group
from Application.create_bot import bot
from ports.db import get_order, add_suggestion, add_question, get_setting
from bot_config import ADMIN_ID


async def send_suggestion(suggestion: str, name: str, id: int) -> None:
    admins_id = (await get_setting("suggestions_group"))
    if admins_id == '' or not (await bot_in_group(admins_id)):
        admins_id = ADMIN_ID
    else:
        admins_id = int(admins_id)

    await bot.send_message(admins_id, f"🔥 <b>Предложение от пользователя '@{name}':</b>🔥\n{suggestion}", parse_mode="html")
    await add_suggestion(name, id, suggestion)


async def send_order(id: int)  -> None:
    admins_id = (await get_setting("orders_group"))
    if admins_id == '' or not (await bot_in_group(admins_id)):
        admins_id = ADMIN_ID
    else:
        admins_id = int(admins_id)
    order_info = await get_order(id)
    products = ''
    for i in order_info[3]:
        products += f"'{i[0]}' "
        if i[2] == '0':
            products += f'{i[1]} единиц - покупка\n'
        elif i[2] == '1':
            products += f'{i[1]} дней - аренда\n'
        elif i[2] == '2':
            products += f'{i[1]} единиц - покупка, цифровой товар\n'
    await bot.send_message(admins_id, "🔥 <b>Новый заказ:</b>🔥", parse_mode="html")
    get_order_keyboard = [
        [InlineKeyboardButton(text='✅ Взять заказ', callback_data=f'{order_info[0]}')]
    ]
    get_order_markup = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=get_order_keyboard)

    str = (
        f"👱‍♂️ <b>Пользователь:</b>\n@{order_info[1]}\n🕒 Дата: {order_info[11]}\n\n🏵 "
        f"<b>Заказ:</b>\n{products}\n\n💵 <b>Цена покупки:</b> {order_info[7]}\n\n💵 <b>Цена аренды:</b> "
        f"{order_info[4]}\n\n💵 <b>Депозит:</b> {order_info[5]}\n\n💰 <b>Цена заказа:</b> {order_info[6]}\n\n📦 "
        f"<b>Метод получения заказа:</b>\n"
    )
    if order_info[8] == '1':
        str += (
            f"🚗 Доставка\n\n🗺 <b> Адрес: </b>\n"
            f"{order_info[9]}\n\n"
        )
    elif order_info[8] == '0':
        str += (
            f"🚶🏻 Самовывоз\n\n"
        )
    elif order_info[8] == '2':
        str += (
            f"🌐 Цифровая покупка - выдаётся администратором в личном чате с покупателем.\n\n"
        )
    if order_info[10] == '1':
        str += f"💸<b>Оплачено картой</b>"
    else:
        str += f"💵<b>Оплата наличкой</b>"
    await bot.send_message(admins_id, text=str, reply_markup=get_order_markup)


async def send_question(question: str, name: str, id: int) -> None:
    admins_id = (await get_setting("questions_group"))
    if admins_id == '' or not (await bot_in_group(admins_id)):
        admins_id = ADMIN_ID
    else:
        admins_id = int(admins_id)
    await bot.send_message(admins_id, f"❓<b>Вопрос от '@{name}':</b>❓\n{question}", parse_mode="html")
    await add_question(name, id, question)


async def new_admin(message: Message) -> None:
    admins_id = int(ADMIN_ID)
    await bot.send_message(admins_id, f"❗<b>Активирован админ-аккаунт!</b>❗\nНик: {message.from_user.username}\nID: {message.from_user.id}")
