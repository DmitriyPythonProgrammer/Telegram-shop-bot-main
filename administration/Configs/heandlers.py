from aiogram import F, types
from aiogram.fsm.context import FSMContext
from Application.admin import *
from Domain.functions import online_product_in_shop, not_online_product_in_shop
from .generator import settings
from .states import Input_Settings
from Framework.Filters import IsAdmin, IsSettings, IsNotCancel, IsSettingsSection
from bot_config import ADMIN_ID
from core.create_bot import dp, bot
from ports.db import update_setting, get_setting
from ..markups import change_settings_markup, cancel_markup, settings_markup, cancel_or_empty_markup, \
    settings_sections_markup


@dp.message(F.text, IsAdmin(), lambda message: message.text == "⚙️ Настройки")
async def settings_menu(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Input_Settings.in_menu)
    await bot.send_message(message.from_user.id, "⚙️ Вы открыли настройки бота", reply_markup=settings_sections_markup)


@dp.message(IsAdmin(), IsSettingsSection(), Input_Settings.in_menu)
async def settings_sections(message: types.Message) -> None:
    await bot.send_message(message.chat.id, f'Вы открыли раздел {message.text}', reply_markup=(await settings_markup(message)))


@dp.message(IsAdmin(), IsSettings(), Input_Settings.in_menu)
async def settings_value(message: types.Message, state: FSMContext) -> None:
    setup = ''
    for i in range(len(settings.settings)):
        if message.text == settings.settings[i][3]:
            setup = settings.settings[i]
            await state.update_data(setup=setup)
    if setup[3] == '🖼️ Стартовое фото':
        await bot.send_message(message.chat.id, text=f"🔧 Значение настройки '{setup[2]}':\n")
        if setup[2] == '':
            await bot.send_message(message.chat.id, text='пусто', reply_markup=change_settings_markup(setup))
        else:
            await bot.send_photo(message.chat.id, photo=setup[2], reply_markup=change_settings_markup(setup))
    else:
        await bot.send_message(message.chat.id, text=f"🔧 Значение настройки '{setup[3]}':\n - {setup[2]}", reply_markup=change_settings_markup(setup))


@dp.message(IsAdmin(), F.text.startswith("🔧 Изменить настройку '"), Input_Settings.in_menu)
async def settings_value(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data['setup'][4] != 0:

        await state.update_data(settings_name=message.text[22:-1])

        if message.text[22:-1] == '🌐 Только онлайн покупки':
            await bot.send_message(message.chat.id, "❗ Внимание! При включении данного режима будет доступна оплата только картой, а продажа будет доступна только цифровых товаров.")
            not_online_products = (await not_online_product_in_shop())
            if not_online_products != False:
                await bot.send_message(message.chat.id, f"❌ Невозможно включить режим:\nОбнаружено, что у вас есть в наличии нецифровые товары, измените их количество в наличии на 0:\n{not_online_products}")
                return
            address = (await get_setting('pickup_address'))
            if address == '':
                await bot.send_message(message.chat.id,
                                       f"❌ Невозможно включить режим:\nПо умолчанию включён способ получения 'самовывоз'. "
                                       f"Но в данный момент не указан адрес. Пожалуйста укажите адрес для самовывоза, а потом измените данную настройку.")
                return

        if message.text[22:-1] == '🚚 Возможность доставки':
            only_online = (await get_setting("only_online"))

            if only_online == '1':
                await bot.send_message(message.chat.id,
                                       "❌ У вас включён режим '🌐 Только онлайн покупки', отключите его чтобы изменить способы получения товара.",
                                       reply_markup=settings_sections_markup)
                return

            pickup = (await get_setting("pickup"))
            if pickup == '0':
                await bot.send_message(message.chat, "❗ Внимание, у вас отключен самовывоз, и если вы отключите и доставку, магазин перестанет принимать все заказы кроме цифровых!")

        if message.text[22:-1] == '📦 Возможность самовывоза':
            only_online = (await get_setting("only_online"))

            if only_online == '1':
                await bot.send_message(message.chat.id,
                                       "❌ У вас включён режим '🌐 Только онлайн покупки', отключите его чтобы изменить способы получения товара.",
                                       reply_markup=settings_sections_markup)
                return
            pickup_address = (await get_setting("pickup_address"))
            if pickup_address == '':
                await bot.send_message(message.chat.id, "❌ Прежде чем включить возможность самовывоза, укажите адрес.", reply_markup=settings_sections_markup)
                return
            delivery = (await get_setting("delivery"))
            if delivery == '0':
                await bot.send_message(message.chat, "❗ Внимание, у вас отключена доставка, и если вы отключите и самовывоз, магазин перестанет принимать все заказы кроме цифровых!")

        if message.text[22:-1] == '🗝️ Ключ администратора':
            if message.from_user.id != ADMIN_ID:
                await bot.send_message(message.chat.id, "❌ Эту настройку может изменить только главный администратор",
                                       reply_markup=settings_sections_markup)
                return

        if message.text[22:-1] == '💵 Оплата принимается наличкой':
            only_online = (await get_setting("only_online"))

            if only_online == '1':
                await bot.send_message(message.chat.id,
                                       "❌ У вас включён режим '🌐 Только онлайн покупки', отключите его чтобы изменить способ оплаты на 'наличные'.",
                                       reply_markup=settings_sections_markup)
                return

            card_payment = (await get_setting("pay_card"))
            if card_payment == '0':
                await bot.send_message(message.chat.id,
                                       "❌ У вас отключена оплата другим способом. Пожалуйста включите другой способ, если хотите изменить текущий.",
                                       reply_markup=settings_sections_markup)
                return

        if message.text[22:-1] == '💳 Оплата принимается картой':
            cash_payment = (await get_setting("pay_cash"))
            if cash_payment == '0':
                await bot.send_message(message.chat.id, "❌ У вас отключена оплата другим способом. Пожалуйста включите другой способ, если хотите изменить текущий.",
                                       reply_markup=settings_sections_markup)
                return

            online_products = (await online_product_in_shop())

            if online_products != False:
                await bot.send_message(message.chat.id, f"❌ В вашем магазине есть цифровые товары.\nОни оплачиваются только картой, поэтому если вы хотите изменить эту настройку и принимать оплату наличными, измените кол-во в наличии на 0 следующих товаров:\n{online_products}",
                                       reply_markup=cancel_or_empty_markup)
                return

        if data['setup'][5] == 1:
            await bot.send_message(message.chat.id, "Введите новое значение или нажмите на кнопку '🚫 Оставить пустым' или нажмите кнопку 'Отмена': ",
                                   reply_markup=cancel_or_empty_markup)
        else:
            await bot.send_message(message.chat.id, "Введите новое значение или нажмите кнопку 'Отмена': ",
                                   reply_markup=cancel_markup)
        await state.set_state(Input_Settings.change)
    else:
        await bot.send_message(message.chat.id, "❌ Данную настройку невозможно изменить ❗",
                               reply_markup=settings_sections_markup)


@dp.message(IsAdmin(), IsNotCancel(), Input_Settings.change)
async def cancel_change_settings(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    value = ''
    if data['setup'][4] == 1 and message.text == '🚫 Оставить пустым':
        value = ''
    else:
        if data['setup'][6] == 'photo':
            if message.photo == None:
                await bot.send_message(message.chat.id, "❌ Отправьте фото", reply_markup=cancel_markup)
                return
            else:
                await update_setting("start_photo", message.photo[0].file_id)
        else:
            if data['setup'][6] == 'int' or data['setup'][6] == 'bool':
                if message.text.isdigit():
                    if data['setup'][6] == 'bool':
                        if int(message.text) == 0 or int(message.text) == 1:
                            value = message.text
                        else:
                            await bot.send_message(message.chat.id, "❌ Введите либо 1 - да, либо 0 - нет", reply_markup=cancel_markup)
                            return None
                    else:
                        value = message.text
                else:
                    await bot.send_message(message.chat.id, "❌ Введите число", reply_markup=cancel_markup)
                    return None
            else:
                value = message.text
    await update_setting((data['setup'][1]), value)
    await state.clear()
    await state.set_state(Input_Settings.in_menu)
    if (await get_setting('start_photo')) == '' and (await get_setting('start_mes')) == '':
        await bot.send_message(message.chat.id, "❗️ Внимание ❗\nОпределено, что обе настройки '🖼️ Стартовое фото' и  '👋🏻 Приветственное сообщение' пустые. Чтобы избежать ошибки, при команде /start будет выводиться стандартное сообщение. Пожалуйста, измените одну из этих двух настроек.")
    await bot.send_message(message.chat.id, "✔️ Значение изменено", reply_markup=settings_sections_markup)


@dp.message(IsAdmin(), IsNotCancel(), Input_Settings.change)
async def cancel_change_settings(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await bot.send_message(message.chat.id, "❗ Вы отменили изменение ❗", reply_markup=settings_sections_markup)






