from ..Configs import *
from bot_config import ADMIN_ID
from .keyboards import *
from aiogram.types import ReplyKeyboardMarkup, CallbackQuery, InlineKeyboardMarkup
from ports.db  import return_admins

menu_markup = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=menu)
main_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=main)
main_admin_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=main_admin)
order_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=order)
basket_main_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=basket_main)
basket_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=basket)
choice_basket_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=choice_basket)
load_markup = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=load)
pick_method_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=pick_method)
buy_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=buy)
pay_method = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=pay)
cash_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, keyboard=cash)
finish_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, keyboard=finish)
admin_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=admin)
sub_res_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=sub_res)
settings_sections_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=(settings.markup_sections()))
cancel_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=cancel)
cancel_or_empty_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=cancel_or_empty)
first_admin_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=first_admin)
buy_or_arend_markup = InlineKeyboardMarkup(resize_keyboard=True, row_width=2, inline_keyboard=buy_or_arend)
add_group_markup = InlineKeyboardMarkup(resize_keyboard=True, row_width=2, inline_keyboard=add_group)


async def settings_markup(message: Message):
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=(await settings.markup_settings(message)))


def change_settings_markup(setup):
    change_settings_btn = KeyboardButton(text=f"🔧 Изменить настройку '{setup[3]}'")
    change_settings = [
        [change_settings_btn],
        [settings_btn],
        [to_admins_menu]
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=change_settings)


async def main_menu_f(output):
    if isinstance(output, Message) or isinstance(output, CallbackQuery):
        user_id = output.from_user.id
    else:
        user_id = output
    if user_id in (await return_admins()) or user_id == ADMIN_ID:
        return main_admin_markup
    return main_markup


def admin_markup_f(output):
    if isinstance(output, Message) or isinstance(output, CallbackQuery):
        user_id = output.from_user.id
    else:
        user_id = output
    if user_id == ADMIN_ID:
        return first_admin_markup
    else:
        return admin_markup


def pay_menu(isUrl=True, url="", bill=""):
    qiwi_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
    if isUrl:
        urlQiwi = [[InlineKeyboardButton(text="Ссылка на оплату", url=url)]]
        qiwi_menu = InlineKeyboardMarkup(row_width=1, inline_keyboard=urlQiwi)
    checkQiwi = InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_{bill}")
    qiwi_menu.add(checkQiwi)
    return qiwi_menu

async def admin_list_markup():
    admin_list = (await return_admins_usernames())
    admin_list_kb = []
    for i in admin_list:
        admin_list_kb.append([KeyboardButton(text=i)])
    admin_list_kb.append([cancel_btn])
    final_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=admin_list_kb)
    return final_markup