from aiogram.types import KeyboardButton, Message

from ports.db import get_setting, truncate_settings, add_setting


class Settings:
    def __init__(self):
        self.sections = {'Main': '👨🏼‍🔧 Основные настройки', 'Messages': '💬 Сообщения', 'Store': '🛍️ Настройки магазина', 'Security': '🔐 Безопасность'}
        # section_name: section_text_for_user
        self.default_settings = []
        self.default_settings.append(['Main', 'language', 'ru', '🌐 Язык бота', 0, 0, 'str'])
        self.default_settings.append(['Main', 'version', '1.0', '💡 Версия бота', 0, 0, 'str'])
        self.default_settings.append(['Security', 'admin_token', 47752021228507955206245, '🗝️ Ключ администратора', 1, 0, 'int'])
        self.default_settings.append(['Security', 'orders_limit', 5, '❗ Лимит на количество заказов в день от одного пользователя', 1, 0, 'int'])
        self.default_settings.append(['Security', 'choices_limit', 10, '❗ Лимит на количество продуктов в корзине', 1, 0, 'int'])
        self.default_settings.append(['Security', 'product_limit', 30, '❗ Лимит на количество товара, дней аренды', 1, 0, 'int'])
        self.default_settings.append(['Security', 'questions_limit', 5, '❗ Лимит на количество вопросов в день', 1, 0, 'int'])
        self.default_settings.append(['Security', 'suggestions_limit', 5, '❗ Лимит на количество предложений в день', 1, 0, 'int'])
        self.default_settings.append(['Store', 'limit_displayed_products', 1, '📋 Кол-во показываемого товара на одной странице магазина', 1, 0, 'int'])
        self.default_settings.append(['Store', 'pickup_address', '', '🏘️ Адрес для самовывоза', 1, 1, 'str'])
        self.default_settings.append(['Store', 'minus_if_rent', 1, '💥 Отнимать кол-во в наличии на 1, если товар арендуют', 1, 0, 'bool'])
        self.default_settings.append(['Store', 'pay_card', 1, '💳 Оплата принимается картой', 1, 0, 'bool'])
        self.default_settings.append(['Store', 'pay_cash', 0, '💵 Оплата принимается наличкой', 1, 0, 'bool'])
        self.default_settings.append(['Store', 'delivery', 0, '🚚 Возможность доставки', 1, 0, 'bool'])
        self.default_settings.append(['Store', 'pickup', 1, '📦 Возможность самовывоза', 1, 0, 'bool'])
        self.default_settings.append(['Store', 'only_online', 1, '🌐 Только онлайн покупки', 1, 0, 'bool'])
        self.default_settings.append(['Messages', 'mess_about_us', 'Мы - самый крутой магазин!', '🌀 О нас', 1, 0, 'str'])
        self.default_settings.append(['Messages', 'mess_faq', 'Часто задаваемые вопросы', '⭐️ FAQ', 1, 0, 'str'])
        self.default_settings.append(['Messages', 'start_photo', '', '🖼️ Стартовое фото', 1, 1, 'photo'])
        self.default_settings.append(['Messages', 'start_mes', 'Привет! И добро пожаловать в наш магазин!', '👋🏻 Приветственное сообщение', 1, 1, 'str'])
        #[section, settings_name, default_value, settings_text_for_user, changeable, may_be_empty, type]
        self.settings = self.default_settings

    async def update(self):
        for i in range(len(self.settings)):
            self.settings[i][2] = (await get_setting(self.settings[i][1]))

    def markup_sections(self):
        result = []
        for i in self.sections.keys():
            result.append([KeyboardButton(text=self.sections[i])])
        result.append([KeyboardButton(text='📟 Админ панель')])
        result.append([KeyboardButton(text='🏠 Главное меню')])
        return result

    async def markup_settings(self, message: Message):
        result = []
        section = ''
        for i in self.sections:
            if self.sections[i] == message.text:
                section = i
        for i in self.settings:
            if i[0] == section:
                result.append([KeyboardButton(text=i[3])])
        result.append([KeyboardButton(text='⚙️ Настройки')])
        result.append([KeyboardButton(text='📟 Админ панель')])

        return result

    async def check_settings(self):
        print("Checking the correctness of the settings...")
        for i in range(len(self.default_settings)):
            setting = (await get_setting(self.default_settings[i][1]))
            if setting is None:
                await self.set_default_settings()
                return 0
        print("Successfully!")

    async def set_default_settings(self):
        print("An error was found in the settings table")
        print("Setting default settings...")
        await truncate_settings()
        for i in self.default_settings:
            await add_setting(i[0], i[1], i[2], i[3], i[4], i[5], i[6])
        print("Successfully!")


settings = Settings()