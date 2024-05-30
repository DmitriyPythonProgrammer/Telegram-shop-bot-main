from aiogram.types import KeyboardButton, InlineKeyboardButton

choose_game = KeyboardButton(text="🛒 Магазин")

menu_btn = KeyboardButton(text="🏠 Главное меню")

about_btn = KeyboardButton(text="🌀 О нас")

faq_btn = KeyboardButton(text="⭐️ FAQ")

ask_btn = KeyboardButton(text="🖌 Спросить")

suggestion_btn = KeyboardButton(text="✉️ Предложение")

basket_btn = KeyboardButton(text="🗑 Корзина")

basket_remove_btn = KeyboardButton(text="✂️ Убрать из корзины")

buy_btn = KeyboardButton(text="🟢 Оформить")

load_more = InlineKeyboardButton(text="Показать ещё", callback_data="load_more")

pickup = KeyboardButton(text="🚶🏻 Самовывоз")

delivery = KeyboardButton(text="🚗 Доставка")

buy1_btn = KeyboardButton(text="💰 Оплатить")

card_btn = KeyboardButton(text="💳 Банковская карта")

cash_btn = KeyboardButton(text="💵 Наличными")

submit_btn = KeyboardButton(text="✅ Подтвердить")

change_btn = KeyboardButton(text="🖌 Изменить метод оплаты")

available_btn = KeyboardButton(text="📪 Редактировать 'в наличии'")

add_new = KeyboardButton(text="🎲 Добавить новый товар")

del_game_btn = KeyboardButton(text="💥 Удалить товар")

sub_add_btn = KeyboardButton(text="✅ Добавить")

reset_btn = KeyboardButton(text="🗯 Сбросить")

to_admins_menu = KeyboardButton(text="📟 Админ панель")

settings_btn = KeyboardButton(text="⚙️ Настройки")

cancel_btn = KeyboardButton(text="❌ Отмена")

empty_btn = KeyboardButton(text="🚫 Оставить пустым")

delete_admin = KeyboardButton(text="☠️ Разжаловать администратора")

information = KeyboardButton(text="⚡️ Важная информация и условия использования")

ban_btn = KeyboardButton(text="💀 Забанить пользователя")

unban_btn = KeyboardButton(text="👼 Разбанить пользователя")

statistic_btn = KeyboardButton(text="📈 Статистика")

add_btn = InlineKeyboardButton(text='✅ Купить', callback_data='add_buy')

arend_btn = InlineKeyboardButton(text='✅ Арендовать', callback_data='add_arend')

orders_group = InlineKeyboardButton(text='Группа для заказов', callback_data='orders_group')

questions_group = InlineKeyboardButton(text='Группа для вопросов', callback_data='questions_group')

suggestions_group = InlineKeyboardButton(text='Группа для предложений', callback_data='suggestions_group')

