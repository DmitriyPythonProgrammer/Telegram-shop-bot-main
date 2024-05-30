import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from Framework.Filters import IsNotCancel, IsNotBanned
from Domain.order_functions import send_suggestion, send_order, send_question
from bot_config import PAYMENT_TOKEN
from ports.db import *
from ports.db import add_data, get_data, update_data, clear_data, \
    add_pay_method, get_product_name, get_product_id, get_setting, update_setting
from Domain.functions import is_available, change_available, print_products, product_to_data, update_price, not_limit, \
    is_only_online
from Application.markups import order_markup, basket_markup, pick_method_markup, buy_markup, pay_method, cash_markup
from Application.create_bot import dp, bot
from Application.markups.markups import main_menu_f, cancel_markup, buy_or_arend_markup
from .states import *
import Application.admin
import Application.Configs


@dp.message(Command("start"))
async def begin(message: types.Message, state: FSMContext):
    first_start = (await get_setting("first_start"))
    await state.clear()
    if first_start == '1' and message.from_user.id == ADMIN_ID:
        await bot.send_message(message.chat.id, "🎉 Поздравляем вас с покупкой универсального бота-магазина для телеграмма! 🎉"
                                                "\n Перед началом продаж, пожалуйста:\n"
                                                "1. Настройте магазин - добавьте товары, отредактируйте настройку 'В наличии'\n"
                                                "2. Измените пароль администратора на свой\n"
                                                "3. Измените стартовое сообщение и фото на свои.\n"
                                                "4. Просмотрите и измените другие настройки под себя.")
        await update_setting("first_start", "0")
        first_start = '0'
    user_info = await bot.get_chat_member(message.chat.id, message.from_user.id)
    name = user_info.user.username
    await add_user(name, user_info.user.id, str(datetime.date.today()))
    await add_data(user_info.user.id)
    start_mes = (await get_setting("start_mes"))
    start_photo = (await get_setting("start_photo"))
    if start_photo != "":
        await bot.send_photo(chat_id=message.chat.id, photo=start_photo, reply_markup=(await main_menu_f(message)))
    if start_mes != "":
        await bot.send_message(message.chat.id, start_mes, reply_markup=(await main_menu_f(message)))
    if start_mes == '' and start_photo == '':
        await bot.send_message(message.chat.id,
                               'Добро пожаловать в бот-магазин для телеграмма! Пожалуйста измени это сообщение в настройках!',
                               reply_markup=(await main_menu_f(message)))


@dp.message(F.text == "🗑 Корзина", IsNotBanned())
async def basket_show(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    games = '' #data[2][название, количество, (0-покупка, 1 - аренда, 2 - цифровой товар), общая сумма за товар]
    if data[2]:
        for i in range(len(data[2])):
            if data[2][i][2] == '1':
                games+=f'🥏 {data[2][i][0]} - 📅 {data[2][i][1]} дней ({data[2][i][3]}💵)\n'
            if data[2][i][2] == '0' or data[2][i][2] == '2':
                games += f'🥏 {data[2][i][0]} '
                if int(data[2][i][1])>1:
                    games += f'- {data[2][i][1]} штук '
                games += f'({data[2][i][3]}💵)'
                games += '\n'
        await bot.send_message(message.chat.id, "<b>🗑 Корзина: </b>\n\n{games}\n\n<b>Сумма покупки:</b> {price}💰\n\n<b>Сумма аренды:</b> {rent}💰\n\n<b>Сумма залога:</b> {deposit_price}💰\n\n<b>Общая сумма:</b> {final_price}💰 ".format(games=games, rent=data[3], final_price=data[5], deposit_price=data[4], price=data[7]),
                        parse_mode="html", reply_markup=basket_markup)
    else:
        await bot.send_message(message.chat.id, "🕸 Корзина пуста")


@dp.message(F.text == "🛒 Магазин")
async def choose_game(message: types.Message, state: FSMContext):
    limit = int((await get_setting("limit_displayed_products")))
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    data[6] = 0
    data[1] = limit
    check = (await checker())

    if check is not None:
        await bot.send_message(message.chat.id, "🛒 Товары в наличии:", reply_markup=order_markup)
        await print_products(message.from_user.id, data[6], limit, data[1])
        data[6] += limit
        data[1] += limit
    else:
        await bot.send_message(message.chat.id, "В наличии ничего нет 😭")
    await state.set_state(Shop.choose)
    await update_data(data)


@dp.message(F.text == "🏠 Главное меню")
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.chat.id, "<b>Вы вышли в главное меню</b>", parse_mode="html", reply_markup=(await main_menu_f(message)))


@dp.message(F.text == "🌀 О нас")
async def about_us(message: types.Message):
    text = (await get_setting("mess_about_us"))
    await bot.send_message(message.chat.id, text, parse_mode="html")


@dp.message(F.text == "⭐️ FAQ")
async def faq(message: types.Message):
    text = (await get_setting("mess_faq"))
    await bot.send_message(message.chat.id, text, parse_mode="html")


@dp.message(F.text == "❌ Отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.chat.id, "❗ Действие отменено ❗", reply_markup=(await main_menu_f(message)), parse_mode="html")


@dp.message(F.text == "🖌 Спросить", IsNotBanned())
async def ask(message: types.Message, state: FSMContext):
    if not (await not_limit(message.from_user.id, 'question')):
        await bot.send_message(message.from_user.id, "❌ Ошибка, вы превысили лимит кол-ва вопросов в день!", reply_markup=(await main_menu_f(message)))
        return 0
    await state.set_state(Ask.question)
    await bot.send_message(message.chat.id, "📋 Введите интересующий вас вопрос или нажмите кнопку 'Отмена'", reply_markup=cancel_markup, parse_mode="html")


@dp.message(F.text == "✂️ Убрать из корзины", IsNotBanned())
async def remove_product(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    rem_day = []
    for item in data[2]:
        product_id = (await get_product_id(item[0]))
        if item[2] == '0' or item[2] == '2':
            rem_day_button = InlineKeyboardButton(text=f"Убрать из корзины покупку '{item[0]}'", callback_data=f'{product_id}')
            rem_day.append([rem_day_button])
        if item[2] == '1':
            rem_day_button = InlineKeyboardButton(text=f"Убрать из корзины аренду '{item[0]}'", callback_data=f'{product_id}')
            rem_day.append([rem_day_button])
    remove_markup = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=rem_day)

    await bot.send_message(message.chat.id, "Что убрать?", reply_markup=remove_markup)
    await state.set_state(Shop.delete)


@dp.message(F.text == "🟢 Оформить", IsNotBanned())
async def register_order(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    if not (await not_limit(message.from_user.id, 'order')):
        await bot.send_message(message.from_user.id, "❌ Ошибка, вы превысили лимит количества заказов в день!", reply_markup=(await main_menu_f(message)))
        return 0
    available = await is_available(data)
    if available != True:
        await bot.send_message(message.chat.id,
                               f"❌ Ошибка, '{available}' больше нет в наличии, либо такого кол-ва нет в наличии! ❌",
                               reply_markup=basket_markup)
        return 0
    if (await is_only_online(data)):
        await bot.send_message(message.chat.id, "🌐 У вас корзине только цифровые товары. Их вам выдадут администраторы в личном чате.", reply_markup=cancel_markup)
        await add_order(data, "2", message.from_user.username)
        await bot.send_message(message.from_user.id, "❗ Для цифровых товаров доступна оплата только картой")
        await card(message, state)
        return 0
    delivery = (await get_setting('delivery'))
    pickup = (await get_setting('pickup'))
    if delivery == '1' and pickup == '1':
        await state.set_state(Shop.pickup_method)
        await bot.send_message(message.chat.id, "🎯 Выберите метод получения заказа", reply_markup=pick_method_markup)
    elif delivery == '1' and pickup == '0':
        await bot.send_message(message.from_user.id, "❗ В данный момент доступна только доставка!")
        await delivery_method(message, state)
    elif delivery == '0' and pickup == '1':
        await bot.send_message(message.from_user.id, "❗ В данный момент доступен только самовывоз!")
        await pickup_method(message, state)
    else:
        await bot.send_message(message.from_user.id,
                               "❌ В данный момент магазин не работает, попробуйте позже.\n"
                               "Просим прощения за предоставленные неудобства и надеемся на ваше понимание ❤️",
                               reply_markup=(await main_menu_f(message)))
        await state.clear()


@dp.message(F.text == "🚶🏻 Самовывоз", Shop.pickup_method)
async def pickup_method(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    pickup_address = (await get_setting("pickup_address"))
    await bot.send_message(message.chat.id, f"🗺 Самовывоз с адреса:\n{pickup_address}<b></b>", parse_mode="html", reply_markup=buy_markup)
    await state.set_state(Shop.pay)
    await add_order(data, "0", message.from_user.username)


@dp.message(F.text == "🚗 Доставка", Shop.pickup_method)
async def delivery_method(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "❗ Доставка оплачивается отдельно\n\nВведите адрес доставки или нажмите кнопку 'Отмена':", reply_markup=cancel_markup, parse_mode="html")
    await state.set_state(Address.address)


@dp.message(F.text == "💰 Оплатить" or F.text == "🖌 Изменить метод оплаты", Shop.pay)
async def to_pay(message: types.Message, state: FSMContext):
    pay_cash = (await get_setting("pay_cash"))
    pay_card = (await get_setting("pay_card"))
    if pay_cash == '1' and pay_card == '1':
        await bot.send_message(message.chat.id, "Выберите способ оплаты:", reply_markup=pay_method)
        await state.set_state(Shop.payment)
    else:
        if pay_cash == '1':
            await bot.send_message(message.from_user.id, "❗ Доступна оплата только наличными",
                                   reply_markup=basket_markup)
            await cash(message, state)
        if pay_card == '1':
            await bot.send_message(message.from_user.id, "❗ Доступна оплата только картой",
                                   reply_markup=basket_markup)
            await card(message, state)


@dp.message(F.text == "💳 Банковская карта", Shop.payment)
async def card(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    available = await is_available(data)
    if available != True:
        await bot.send_message(message.chat.id,
                               f"❌ Ошибка, '{available}' больше нет в наличии, либо такого кол-ва нет в наличии! ❌",
                               reply_markup=basket_markup)
        return 0
    await bot.send_message(message.chat.id, "✅ Вы выбрали оплату картой")
    title =""
    for i in data[2]:
        title+=f"Товар:'{i[0]}', количество: {i[1]}\n"
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Покупка товаров",
        description=title,
        provider_token=PAYMENT_TOKEN,
        currency='rub',
        is_flexible=False,
        prices=[LabeledPrice(label='Общая сумма:', amount=data[5]*100)],
        start_parameter='time-machine-example',
        payload=str(data[0])
    )
    await state.update_data(id=data[0])
    await state.set_state(None)


@dp.message(F.text == "💵 Наличными", Shop.payment)
async def cash(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "✅ Вы выбрали оплату наличными", reply_markup=cash_markup)
    await add_pay_method("0", message.from_user.id)
    await state.set_state(Shop.finish)


@dp.message(F.text == "✅ Подтвердить", Shop.finish)
async def finish(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "❇️ Ваш заказ принят, скоро с вами свяжется продавец", reply_markup=(await main_menu_f(message.from_user.id)))
    order_info = await get_order(message.from_user.id)
    if order_info[10] == '0':
        data = (await get_data(message.from_user.id))
        if data == False:
            await bot.send_message(message.from_user.id,
                                   "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
            await state.clear()
            return 0
        available = await is_available(data)
        if available != True:
            await bot.send_message(message.chat.id,
                                   f"❌ Ошибка, '{available}' больше нет в наличии, либо такого кол-ва нет в наличии! ❌",
                                   reply_markup=basket_markup)
            return 0
        await change_available(data)
    await send_order(message.from_user.id)
    await clear_data(message.from_user.id)
    await state.clear()


@dp.message(F.text == "✉️ Предложение", IsNotBanned())
async def suggestion(message: types.Message, state: FSMContext):
    if not (await not_limit(message.from_user.id, 'suggestion')):
        await bot.send_message(message.from_user.id, "❌ Ошибка, вы превысили лимит кол-ва предложений в день!", reply_markup=(await main_menu_f(message)))
        return 0
    await state.set_state(Suggestion.suggestion)
    await bot.send_message(message.chat.id, "⌨️ Введите то, что вы бы хотели видеть у нас в сервисе или нажмите кнопку 'Отмена'", reply_markup=cancel_markup)
    

@dp.message(Address.address, IsNotCancel())
async def load_address(message: types.Message, state: FSMContext):
    data = (await get_data(message.from_user.id))
    if data == False:
        await bot.send_message(message.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    await bot.send_message(message.chat.id, "✅ Адрес записан", reply_markup=buy_markup)
    await add_order(data, "1", message.from_user.username, message.text)
    await state.set_state(Shop.pay)


@dp.message(Suggestion.suggestion, IsNotCancel())
async def load_answer(message: types.Message, state: FSMContext):
    suggestion = message.text
    await bot.send_message(message.chat.id, "📤 Спасибо, ваше предложение сохранено", reply_markup=(await main_menu_f(message)))
    await send_suggestion(suggestion, message.from_user.username, message.from_user.id)
    await state.clear()


@dp.message(Ask.question, IsNotCancel())
async def load_suggestion(message: types.Message, state: FSMContext):
    question = message.text
    await bot.send_message(message.chat.id, "✳️ Ваш вопрос сохранен и отправлен продавцу", reply_markup=(await main_menu_f(message)))
    await send_question(question, message.from_user.username, message.from_user.id)
    await state.clear()


@dp.callback_query(Shop.delete, IsNotBanned())
async def delete_product(callback: types.CallbackQuery, state: FSMContext):
    data = (await get_data(callback.from_user.id))
    product_name = (await get_product_name(int(callback.data)))
    if data == False:
        await bot.send_message(callback.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    data_mod = data
    for i in range(len(data[2])):
        if data[2][i][0] == product_name:
            data_mod[2].pop(i)
            await bot.send_message(callback.from_user.id, f"✔️ '{product_name}' был удалён из корзины", reply_markup=basket_markup)
            await update_price(data_mod)
            await state.clear()
            return 0
    await bot.send_message(callback.from_user.id, "❌ В вашей корзине нет такого товара!")
    await state.clear()


@dp.callback_query(Shop.choose, IsNotBanned(), lambda c: c.data != "load_more")
async def buy_or_arend(callback: types.CallbackQuery, state: FSMContext):
    data = (await get_data(callback.from_user.id))
    product_name = (await get_product_name(int(callback.data)))
    if data == False:
        await bot.send_message(callback.from_user.id,
                               "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    limit = int((await get_setting("choices_limit")))
    if len(data[2]) >= limit:
        await bot.send_message(callback.from_user.id, "❌ Ошибка! Вы достигли лимита товаров в корзине", reply_markup=(await main_menu_f(callback)))
        return 0
    info = await get_info(product_name)
    await state.update_data(product_name=product_name)
    if info[1] != 0 and info[2] != 0:
        await state.set_state(Shop.buy_or_arend)
        await bot.send_message(callback.from_user.id, '❗ Выберите, что вы хотите сделать:', reply_markup=buy_or_arend_markup)
    else:
        if info[1] != 0:
            await state.update_data(type=0)
            await bot.send_message(callback.from_user.id, '✏️ Введите количество, которое вы хотите купить')
        elif info[2] != 0:
            await state.update_data(type=1)
            await bot.send_message(callback.from_user.id, '✏️ Введите количество дней, на которое вы хотите арендовать товар')
        if info[4] == 1:
            await state.update_data(type=2)
        await state.set_state(Shop.count)


@dp.callback_query(Shop.buy_or_arend, IsNotBanned())
async def counts(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "add_buy":
        await state.update_data(type=0)
        await bot.send_message(callback.from_user.id, '✏️ Введите количество, которое вы хотите купить')
    elif callback.data == 'add_arend':
        await state.update_data(type=1)
        await bot.send_message(callback.from_user.id, '✏️ Введите количество дней, на которое вы хотите арендовать товар')
    await state.set_state(Shop.count)


@dp.message(Shop.count)
async def add_product(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) > 0:
            data = (await get_data(message.from_user.id))
            if data == False:
                await bot.send_message(message.from_user.id,
                                       "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
                await state.clear()
                return 0
            data_product = await state.get_data()
            data = await product_to_data(data, data_product['product_name'], int(message.text), data_product['type'])
            if data == False:
                await bot.send_message(message.from_user.id, "❌ Ошибка! вы не можете добавить такое количество!", reply_markup=(await main_menu_f(message)))
                return 0
            await update_data(data)
            await update_price(data)
            await bot.send_message(message.from_user.id, "🟢 Успешно добавлено!", reply_markup=(await main_menu_f(message)))
        else:
            await bot.send_message(message.from_user.id,
                                   f'❌ Невозможно добавить количество {message.text}. Добавьте товар в корзину заного.',
                                   reply_markup=(await main_menu_f(message)))
    else:
        await bot.send_message(message.from_user.id, '❌ Нужно ввести число! Добавьте товар в корзину заного.', reply_markup=(await main_menu_f(message)))


@dp.callback_query(lambda c: c.data)
async def load_more(callback: types.CallbackQuery, state: FSMContext):
    limit = int((await get_setting("limit_displayed_products")))
    data = (await get_data(callback.from_user.id))
    if data == False:
        await bot.send_message(callback.from_user.id, "📛 Ошибка! 📛\nКажется, бот потерял ваши данные. Для их восстановления напишите '/start'")
        await state.clear()
        return 0
    if callback.data == "load_more":
        await print_products(callback.from_user.id, data[6], limit, data[1])
        data[6] += limit
        data[1] += limit

    await update_data(data)
