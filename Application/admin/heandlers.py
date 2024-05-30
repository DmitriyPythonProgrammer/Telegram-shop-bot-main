import datetime
from aiogram.enums import ContentType
from aiogram.filters import Command
from ports.db import *
from Domain.order_functions import new_admin, send_order
from aiogram import types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from .states import *
from aiogram.fsm.context import FSMContext
from Domain.functions import change_available, is_number, is_photo
from ..markups import cancel_markup, admin_markup_f, add_group_markup, main_menu_f, sub_res_markup, admin_list_markup
from ..create_bot import bot, dp
from Framework.Filters import IsAdmin, IsNotCancel, IsFirstAdmin, IsGroup


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id,
        f"✅ Оплата {message.successful_payment.total_amount / 100} {message.successful_payment.currency} успешна!")
    id = int(message.successful_payment.invoice_payload)
    data = (await get_data(id))
    await change_available(data)
    await add_pay_method("1", id)
    await bot.send_message(message.chat.id, "❇️ Ваш заказ принят, скоро с вами свяжется продавец",
                           reply_markup=(await main_menu_f(message.from_user.id)))
    await send_order(message.from_user.id)
    await clear_data(message.from_user.id)
    await state.clear()


@dp.message(IsGroup())
async def group(message: types.Message):
    if message.text == "/start":
        await bot.send_message(message.chat.id, "❗ Внимание! Бот работает только в личном чате с ним.")
    if message.text == "/add":
        await bot.send_message(message.chat.id, "❗ Выберите, какую роль будет играть этот чат:", reply_markup=add_group_markup)


@dp.callback_query(IsGroup(), lambda callback: "orders_group" in callback.data)
async def orders_group(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, "❗ Данная группа теперь будет использоваться для приёма заказов.")
    await update_setting("orders_group", str(callback.message.chat.id))


@dp.callback_query(IsGroup(), lambda callback: "questions_group" in callback.data)
async def orders_group(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, "❗ Данная группа теперь будет использоваться для приёма вопросов.")
    await update_setting("questions_group", str(callback.message.chat.id))


@dp.callback_query(IsGroup(), lambda callback: "suggestions_group" in callback.data)
async def orders_group(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, "❗ Данная группа теперь будет использоваться для приёма предложений.")
    await update_setting("suggestions_group", str(callback.message.chat.id))


@dp.callback_query(IsGroup())
async def get_order_admin(callback: types.CallbackQuery):
     order_info = (await get_order_by_id(int(callback.data)))
     await bot.send_message(callback.message.chat.id, f"✅ Администратор {callback.from_user.username} взял заказ пользователя {order_info[0]} от {order_info[1]} числа!")
     await bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id)


@dp.message(Command('stop'), IsFirstAdmin())
async def stop(message: Message):
    await dp.stop_polling()


@dp.message(F.text == "📈 Статистика", IsAdmin())
async def statistic(message: Message):
    all_users = (await return_all_users())
    user_registers_day = 0
    user_registers_week = 0
    user_registers_month = 0
    today_date = datetime.date.today()
    for i in all_users:
        date_datetime = datetime.datetime.strptime(i[3], "%Y-%m-%d").date()
        if date_datetime == today_date:
            user_registers_day += 1
        if (today_date - date_datetime).days <= 7:
            user_registers_week += 1
        if (today_date - date_datetime).days <= 30:
            user_registers_month += 1
    all_orders = (await return_all_orders())
    order_registers_day = 0
    order_registers_week = 0
    order_registers_month = 0
    for i in all_orders:
        date_datetime = datetime.datetime.strptime(i[11], "%Y-%m-%d").date()
        if date_datetime == today_date:
            order_registers_day += 1
        if (today_date - date_datetime).days <= 7:
            order_registers_week += 1
        if (today_date - date_datetime).days <= 30:
            order_registers_month += 1
    count_users = len(all_users)
    count_orders = len(all_orders)
    count_bans = len((await return_all_bans()))
    count_admins = len((await return_admins()))
    await bot.send_message(message.from_user.id, f"👨🏻‍💻 Статистика 👨🏻‍💻\n\n"
                                                 f"За день:\n"
                                                 f"Количество новых пользователей: {user_registers_day}\n"
                                                 f"Количество новых заказов: {order_registers_day}\n\n"
                                                 f"За неделю:\n"
                                                 f"Количество новых пользователей: {user_registers_week}\n"
                                                 f"Количество новых заказов: {order_registers_week}\n\n"
                                                 f"За месяц:\n"
                                                 f"Количество новых пользователей: {user_registers_month}\n"
                                                 f"Количество новых заказов: {order_registers_month}\n\n"
                                                 f"Общая статистика:"
                                                 f"Количество пользователей: {count_users}\n"
                                                 f"Количество заказов: {count_orders}\n"
                                                 f"Количество забаненных: {count_bans}\n"
                                                 f"Количество администраторов бота: {count_admins}", reply_markup=admin_markup_f(message))


@dp.message(F.text == '💀 Забанить пользователя', IsAdmin())
async def ban(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Введите юзернейм пользователя без пробелов, с символом @ либо нажмите кнопку 'Отмена'.\nПример: @Pr1zrak0", reply_markup=cancel_markup)
    await state.set_state(ManageUser.ban_user)


@dp.message(F.text == '👼 Разбанить пользователя', IsAdmin())
async def unban(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Введите юзернейм пользователя без пробелов, с символом @ либо нажмите кнопку 'Отмена'.\nПример: @Pr1zrak0", reply_markup=cancel_markup)
    await state.set_state(ManageUser.unban_user)


@dp.message(F.text == "📟 Админ панель", IsAdmin())
async def admin_panel(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.from_user.id, "📟 Админ панель, выберите действие:", reply_markup=admin_markup_f(message))


@dp.message(F.text, lambda message: "/admin" in message.text)
async def admin_reg(message: types.Message):
    ADMIN_TOKEN = (await get_setting("admin_token"))
    if f"/admin {ADMIN_TOKEN}" in message.text:
        is_admin = IsAdmin()
        if not (await is_admin(query_or_message=message)):
            await add_admin(message.from_user.id, message.from_user.username)
            await bot.send_message(message.from_user.id, "📟 Админ панель, выберите действие:", reply_markup=admin_markup_f(message))
            await new_admin(message)
            await message.delete()
        else:
            await bot.send_message(message.from_user.id, "❗ Вы уже администратор! ❗", reply_markup=admin_markup_f(message))
            await message.delete()


@dp.message(F.text == '⚡️ Важная информация и условия использования', IsAdmin())
async def information(message: Message):
    await bot.send_message(message.chat.id, "⚡ Важная информация и условия использования ⚡\n"
                                            "Корзина пользователя и некоторые другие данные хранятся в оперативной памяти, "
                                            "поэтому бот следует иногда перезагружать."
                                            " После перезагрузки корзина сбросится.\n\n"
                                            "При возникновении явных ошибок, Гл. Администратор, айди которого записан в боте, должен"
                                            " отключить бота командой /stop и отправить отзыв об ошибке создателю - @Pr1zrak0.\n\n"
                                            "Напоминаем, что создатель бота не несёт ответственность за убытки, потерю денежных средств, информацию,"
                                            "полученную при работе с ботом."
                                            "Также за любые противозаконные действия, связанные с ботом, ответственность несёт тот, кто приобрёл бота.")


@dp.message(F.text == "🎲 Добавить новый товар", IsAdmin())
async def adm_start(message: types.Message, state: FSMContext):
    await state.set_state(AddGame.name)
    await bot.send_message(message.chat.id, "📖 Введите название товара или нажмите кнопку 'Отмена' для выхода.", reply_markup=cancel_markup)


@dp.message(AddGame.name, IsAdmin(), IsNotCancel())
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddGame.online_product)
    await bot.send_message(message.chat.id, "🌐 Является ли этот товар цифровым? 1 - да, 0 - нет, 'Отмена' для выхода. Для таких товаров недоступна доставка и самовывоз,"
                                            " администраторы сами отправляют товар клиенту по интернету. (Пример: код, покупка игровой валюты)", reply_markup=cancel_markup)


@dp.message(AddGame.online_product, IsAdmin(), IsNotCancel())
async def load_name(message: types.Message, state: FSMContext):
    if not(message.text == '0' or message.text == '1'):
        await bot.send_message(message.chat.id, "❌ Введите либо 1, либо 0. 1- да, 0 - нет.")
        await state.set_state(AddGame.online_product)
        return 0
    await state.update_data(online_product=message.text)
    await state.set_state(AddGame.price)
    await bot.send_message(message.chat.id, "💸 Теперь введите цену покупки. 0 - товар не продаётся. 'Отмена' для выхода.", reply_markup=cancel_markup)


@dp.message(AddGame.price, IsAdmin(), IsNotCancel())
async def load_name(message: types.Message, state: FSMContext):
    if not (await is_number(message)):
        await state.set_state(AddGame.price)
        return 0

    if int(message.text)<0:
        await bot.send_message(message.chat.id, "❌ Не может быть меньше 0! Попробуйте ещё раз или нажмите 'Отмена'",
                               reply_markup=cancel_markup)
        await state.set_state(AddGame.price)
        return 0

    await state.update_data(price=message.text)
    await state.set_state(AddGame.price_day)
    await bot.send_message(message.chat.id, "💸 Теперь введите цену аренды за сутки. 0 - товар не арендуется. 'Отмена' для выхода.", reply_markup=cancel_markup)


@dp.message(AddGame.price_day, IsAdmin(), IsNotCancel())
async def load_price_day(message: types.Message, state: FSMContext):

    if not (await is_number(message)):
        await state.set_state(AddGame.price_day)
        return 0

    if int(message.text) < 0:
        await bot.send_message(message.chat.id, "❌ Не может быть меньше 0! Попробуйте ещё раз или нажмите 'Отмена'",
                               reply_markup=cancel_markup)
        await state.set_state(AddGame.price_day)
        return 0
    await state.update_data(day_price=message.text)
    if message.text != '0':
        await state.set_state(AddGame.deposit)
        await bot.send_message(message.chat.id, "💰 Теперь введите сумму залога. 0 - товар не арендуется. 'Отмена' для выхода.", reply_markup=cancel_markup)
    else:
        await state.update_data(deposit='0')
        await state.set_state(AddGame.photo)
        await bot.send_message(message.chat.id, "🏞 Теперь загрузите фото товара или нажмите кнопку 'Отмена' для выхода.", reply_markup=cancel_markup)


@dp.message(AddGame.deposit, IsAdmin(), IsNotCancel())
async def load_deposit(message: types.Message, state: FSMContext):

    if not (await is_number(message)):
        await state.set_state(AddGame.deposit)
        return 0

    if int(message.text) < 0:
        await bot.send_message(message.chat.id, "❌ Не может быть меньше 0! Попробуйте ещё раз или нажмите 'Отмена'",
                               reply_markup=cancel_markup)
        await state.set_state(AddGame.deposit)
        return 0

    await state.update_data(deposit=message.text)
    await state.set_state(AddGame.photo)
    await bot.send_message(message.chat.id, "🏞 Теперь загрузите фото товара или нажмите кнопку 'Отмена' для выхода.", reply_markup=cancel_markup)


@dp.message(AddGame.photo,  IsAdmin(), IsNotCancel())
async def load_photo(message: types.Message, state: FSMContext):
    if not (await is_photo(message)):
        await bot.send_message(message.chat.id, "❌ Отправьте фото! Попробуйте ещё раз или нажмите 'Отмена'", reply_markup=cancel_markup)
        await state.set_state(AddGame.photo)
        return 0
    await state.update_data(photo=message.photo[0].file_id)
    data = await state.get_data()
    await bot.send_message(message.chat.id, "📋 Введенная информация:", reply_markup=sub_res_markup)
    await bot.send_message(message.chat.id, f"Название: {data['name']}\nЦена покупки: {data['price']}\nЦена за день: {data['day_price']}\nЗалог: {data['deposit']}")
    await state.set_state(AddGame.finish)


@dp.message(F.text == "✅ Добавить", IsAdmin(), AddGame.finish)
async def add_games(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_product(data['name'], data['day_price'], data['deposit'], data['photo'], data['price'], data['online_product'])
    await bot.send_message(message.chat.id, "🟢 Товар добавлен в базу данных", reply_markup=admin_markup_f(message))
    await state.clear()


@dp.message(F.text == "🗯 Сбросить", IsAdmin())
async def reset_info(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, "📂 Изменения сброшены", reply_markup=admin_markup_f(message))
    await state.clear()


@dp.message(F.text == "💥 Удалить товар", IsAdmin())
async def delete_game(message: types.Message, state: FSMContext):
    products_list = []
    products = (await get_products_id_name())
    if products:
        for i in products:
            products_list.append([InlineKeyboardButton(text=i[0], callback_data=f'{i[1]}')])
        products_markup = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=products_list)
        await bot.send_message(message.chat.id, "⌨️ Выбери название товара, который нужно удалить", reply_markup=products_markup)
        await state.set_state(ChangeGame.delete)
    else:
        await bot.send_message(message.chat.id, "🔴 Сначала добавьте товары!", reply_markup=admin_markup_f(message))


@dp.message(F.text == "📪 Редактировать 'в наличии'", IsAdmin())
async def set_av_name(message: types.Message, state: FSMContext):
    products_list = []
    products = (await get_products_id_name())
    if products:
        for i in products:
            products_list.append([InlineKeyboardButton(text=i[0], callback_data=f'{i[1]}')])
        products_markup = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=products_list)
        await bot.send_message(message.chat.id, "🏷 Выбери название товара, который нужно поставить 'в наличии'", reply_markup=products_markup)
        await state.set_state(ChangeGame.change_count)
    else:
        await bot.send_message(message.chat.id, "🔴 Сначала добавьте товары!", reply_markup=admin_markup_f(message))


@dp.message(F.text == '☠️ Разжаловать администратора', IsFirstAdmin(), IsAdmin())
async def del_admin_menu(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Чтобы удалить администратора, выберите его ник из списка: ", reply_markup=(await admin_list_markup()))
    await state.set_state(DeleteAdmin.delete_admin)


@dp.message(F.text, DeleteAdmin.delete_admin, IsNotCancel(), IsFirstAdmin(), IsAdmin())
async def del_admin(message: Message, state: FSMContext):
    if message.text in (await return_admins_usernames()):
        await delete_admin(message.text)
        await bot.send_message(message.chat.id, f"✔️ Администратор {message.text} был удалён.", reply_markup=admin_markup_f(message))
    else:
        await bot.send_message(message.chat.id, f"❌️ Администратора с данным ником не существует ❌", reply_markup=admin_markup_f(message))
    await state.clear()


@dp.message(ManageUser.ban_user, IsAdmin(), IsNotCancel())
async def ban_user(message: Message, state: FSMContext):
    if message.text.count(' ') != 0 or message.text.count('@') != 1:
        await bot.send_message(message.from_user.id, "❌ Ошибка! Неправильно введён юзернейм", reply_markup=admin_markup_f(message))
        return 0
    username = message.text[1:]
    id = (await get_user_id(username))
    admins_id = (await return_admins())
    if id in admins_id:
        await bot.send_message(message.from_user.id, "❌ Ошибка! Невозможно забанить другого администратора.\nЧтобы это сделать, главный администратор должен сначала разжаловать его.", reply_markup=admin_markup_f(message))
        return 0
    if (await is_banned(id)):
        await bot.send_message(message.from_user.id, "❌ Ошибка! Пользователь уже забанен!", reply_markup=admin_markup_f(message))
        return 0
    await bot.send_message(message.from_user.id, f"✔️ Пользователь '{username}' был успешно забанен.", reply_markup=admin_markup_f(message))
    await add_ban(username, id)
    await state.set_state(None)


@dp.message(ManageUser.unban_user, IsAdmin(), IsNotCancel())
async def unban_user(message: Message):
    if message.text.count(' ') != 0 or message.text.count('@') != 1:
        await bot.send_message(message.from_user.id, "❌ Ошибка! Неправильно введён юзернейм", reply_markup=admin_markup_f(message))
        return 0
    username = message.text[1:]
    if not (await is_banned(username)):
        await bot.send_message(message.from_user.id, "❌ Ошибка! Пользователь не забанен!", reply_markup=admin_markup_f(message))
        return 0
    await bot.send_message(message.from_user.id, f"✔️ Пользователь '{username}' был успешно разбанен.", reply_markup=admin_markup_f(message))
    await un_ban(username)


@dp.message(IsAdmin(), ChangeGame.count, lambda message: message.text.isdigit(), IsNotCancel())
async def set_av(message: types.Message, state: FSMContext):
    if not (await is_number(message)):
        await state.set_state(AddGame.photo)
        return 0
    data = await state.get_data()
    id = (await get_product_id(data['product_name']))
    product = (await get_product(id))
    if product[9] == 0:
        only_online = (await get_setting("only_online"))
        if only_online == '1' and message.text != '0':
            await bot.send_message(message.chat.id,
                                   "❌ У вас включен режим '🌐 Только онлайн покупки'. Если вы хотите добавить в наличие нецифровой товар, отключите этот режим. Если вы ошиблись, попробуйте снова, если нет, отмените добавление товара и измените настройки.",
                                   reply_markup=cancel_markup)
            return 0
    else:
        pay_card = (await get_setting("pay_card"))
        if pay_card == '0':
            await bot.send_message(message.chat.id,
                                   "❌ Это цифровой товар, который может быть оплачен только картой. У вас отключена оплата картой, поэтому добавить в наличие невозможно.",
                                   reply_markup=cancel_markup)
            return 0

    if int(message.text)<0:
        await bot.send_message(message.chat.id, "❌ Невозможно добавить значение меньше 0!", reply_markup=admin_markup_f(message))
        return 0
    await set_available(data['product_name'], int(message.text))
    await state.clear()
    await bot.send_message(message.chat.id, f"🎉 Теперь кол-во '{data['product_name']}' в наличии: {(await return_available(data['product_name']))[0]}", reply_markup=admin_markup_f(message))


@dp.callback_query(IsAdmin(), ChangeGame.delete)
async def delete_game_db(callback: types.CallbackQuery):
    product_name = (await get_product_name(int(callback.data)))
    await callback.answer(text=f"Вы выбрали '{product_name}' ")
    await del_game(product_name)
    await bot.send_message(callback.message.chat.id, f"☄️ Товар '{product_name}' удален из базы данных")


@dp.callback_query(IsAdmin(), ChangeGame.change_count)
async def set_av(callback: types.CallbackQuery, state: FSMContext):
    product_name = (await get_product_name(int(callback.data)))
    await bot.send_message(callback.from_user.id, text=f"Вы выбрали '{product_name}'.\nВ данный момент кол-во в наличии: {(await return_available(product_name))[0]}")
    await state.update_data(product_name=product_name)
    await state.set_state(ChangeGame.count)
    await bot.send_message(callback.message.chat.id, f"А теперь введите новое значение, или нажми 'Отмена'", reply_markup=cancel_markup)
