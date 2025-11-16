from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils import config
from data import get_user, User

class IsGroup(BoundFilter):

    async def check(self, message: types.Message):
        return message.chat.type in (types.ChatType.GROUP,
                                     types.ChatType.SUPERGROUP)


class IsPrivate(BoundFilter):

    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        return str(message.from_user.id) in config.config("admin_id")

class IsBan(BoundFilter):
    async def check(self, message: types.Message):
        if await get_user(message.from_user.id):
            return bool(User(message.from_user.id).ban != 'yes')
        else:
            return await get_user(message.from_user.id)