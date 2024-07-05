import datetime
from aiogram import types
from Application.create_bot import bot
from ports.db import *
from Application.markups import *


async def update_price(data: list) -> None:
    price = 0
    rent_price = 0
    final_deposit = 0
    for i in range(len(data[2])):
        info = await get_info(data[2][i][0])
        data[2][i][3] = 0
        if data[2][i][2] == '0' or data[2][i][2] == '2':
            price += int(data[2][i][1])*int(info[1])
            data[2][i][3] += price
        else:
            rent_price += int(data[2][i][1]) * int(info[2])
            final_deposit += int(info[3])
            data[2][i][3] += rent_price
            data[2][i][3] += final_deposit
        data[2][i][3] = str(data[2][i][3])

    data[3] = rent_price
    data[4] = final_deposit
    data[7] = price
    data[5] = price+rent_price+final_deposit
    await update_data(data)


async def product_to_data(data: list, product_name: str, product_count: int, type: str) -> list | bool:
    limit = int((await get_setting("product_limit")))
    if product_count > limit:
        return False
    for i in range(len(data[2])):
        if data[2][i][0] == product_name:
            if data[2][i][2] == str(type):
                if int(data[2][i][1])+product_count > limit:
                    return False
                data[2][i][1] = str(int(data[2][i][1])+product_count)
                return data
    data[2].append([product_name, str(product_count), str(type), '0'])
    return data


async def is_available(data: list) -> bool | any:
    for i in data[2]:
        if i[2] == '0':
            if (await return_available(i[0]))[0] - int(i[1]) < 0:
                return i[0]
        else:
            if (await return_available(i[0]))[0] - 1 < 0:
                return i[0]
    return True


async def change_available(data: list) -> None:
    minus_if_rent = (await get_setting("minus_if_rent"))
    for i in data[2]:
        if i[2] == '0' or i[2] == '2':
            await add_value(i[0], -int(i[1]))
        else:
            if minus_if_rent == '1':
                await add_value(i[0], -1)


async def print_products(id: int, offset: int, limit: int, showed: int) -> None:
    for obj in await return_products(offset, limit):
        text = 'Ошибка!'
        action = 'Ошибка!'
        if obj[8] != 0 and obj[3] != 0:
            action = 'Купить/Арендовать'
            text = f'‎\n🥏 <b>{obj[1]}</b>\n\n'
            text += f'🔹 Цена покупки: {obj[8]}\n\n'
            text += f'🔹 Цена за день: {obj[3]}\n\n'
            if obj[4] != 0:
                text += f'🔹 Залог: {obj[4]}\n\n'
            text += f'🔹 Осталось в наличии: {obj[2]}'
        elif obj[3] != 0:
            action = 'Арендовать'
            text = f'‎\n🥏 <b>{obj[1]}</b>\n\n'
            text += f'🔹 Цена за день: {obj[3]}\n\n'
            if obj[4] != 0:
                text += f'🔹 Залог: {obj[4]}\n\n'
            text += f'🔹 Осталось в наличии: {obj[2]}'
        elif obj[8] != 0:
            action = 'Купить'
            text = f'‎\n🥏 <b>{obj[1]}</b>\n\n'
            text += f'🔹 Цена покупки: {obj[8]}\n\n'
            text += f'🔹 Осталось в наличии: {obj[2]}'

        buy_btn = InlineKeyboardButton(text=f"{action} '{obj[1]}'", callback_data=f'{obj[0]}')
        add = [
            [buy_btn]
        ]
        add_markup = InlineKeyboardMarkup(resize_keyboard=True, row_width=1, inline_keyboard=add)
        await bot.send_photo(chat_id=id, photo=obj[5], reply_markup=add_markup)
        await bot.send_message(chat_id=id, text=text)
    row_counter = await return_count_products()
    counter = row_counter[0]
    if counter > showed and counter != showed:
        await bot.send_message(id, f"Показано <b>{showed}</b> товаров из <b>{counter}</b>", reply_markup=load_markup)
    else:
        await bot.send_message(id, f"Показано <b>{showed}</b> товаров из <b>{counter}</b>")


async def not_limit(id: int, item: str) -> bool:
    dates = 0
    limit = 1
    if item == 'order':
        limit = int((await get_setting("orders_limit")))
        dates = (await return_all_orders_date(id))

    if item == 'suggestion':
        limit = int((await get_setting("suggestions_limit")))
        dates = (await return_all_suggestions_date(id))

    if item == 'question':
        limit = int((await get_setting("questions_limit")))
        dates = (await return_all_questions_date(id))

    date_now = datetime.date.today()
    count = 0
    if len(dates) < limit:
        return True
    for i in dates:
        datetime_date = datetime.datetime.strptime(i[0], "%Y-%m-%d").date()
        if date_now == datetime_date:
            count += 1
    if count >= limit:
        return False
    else:
        return True


async def is_only_online(data: list) -> bool:
    for i in data[2]:
        if i[2] == '0' or i[2] == '1':
            return False
    return True

async def is_number(message: types.Message) -> bool:
    if message.text.isdigit():
        return True
    else:
        await bot.send_message(message.from_user.id, "❌ Введите число", reply_markup=cancel_markup)
        return False


async def is_photo(message: types.Message) -> bool:
    if message.photo != None:
        return True
    else:
        await bot.send_message(message.from_user.id, "❌ Отправьте фото", reply_markup=cancel_markup)
        return False


async def bot_in_group(group_id: int) -> bool:
    try:
        await bot.get_chat_member(chat_id=group_id, user_id=bot.id)
        return True
    except:
        return False

async def online_product_in_shop() -> bool | str:
    products = (await get_all_products())
    input = ''
    for i in products:
        if i[2] != 0 and i[9] == 1:
            input += f"{i[1]}\n"
    if input == '':
        return False
    else:
        return input


async def not_online_product_in_shop() -> bool | str:
    products = (await get_all_products())
    input = ''
    for i in products:
        if i[2] != 0 and i[9] == 0:
            input += f"{i[1]}\n"
    if input == '':
        return False
    else:
        return input