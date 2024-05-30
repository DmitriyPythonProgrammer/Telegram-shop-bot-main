from typing import Union
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from Application.Configs import settings
from bot_config import ADMIN_ID
from ports.db import return_admins, get_data, get_info, is_banned


class IsAdmin(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        return query_or_message.from_user.id in (await return_admins()) or query_or_message.from_user.id == ADMIN_ID


class IsSettingsSection(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        names = (settings.sections[i] for i in settings.sections.keys())
        if query_or_message.text in names:
            return True
        return False


class IsSettings(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        names = (settings.settings[i][3] for i in range(len(settings.settings)))
        if query_or_message.text in names:
            return True
        return False


class IsNotCancel(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        return not "❌ Отмена" == query_or_message.text


class IsFirstAdmin(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        return query_or_message.from_user.id == ADMIN_ID


class IsProductInChoices(Filter):
    async def __call__(self, query: CallbackQuery):
        data = (await get_data(query.from_user.id))
        if data == False:
            return False
        for i in data[2]:
            if i[1] == query.data:
                return True
        return False


class IsProduct(Filter):
    async def __call__(self, query: CallbackQuery):
        if await get_info(query.data):
            return True
        else:
            return False


class IsNotBanned(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        if (await is_banned(query_or_message.from_user.username)):
            return False
        else:
            return True


class IsGroup(Filter):
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]):
        if isinstance(query_or_message, Message):
            if query_or_message.chat.type != 'private':
                return True
        else:
            if query_or_message.message.chat.type != 'private':
                return True
        return False

