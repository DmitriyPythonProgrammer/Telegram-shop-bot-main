from aiogram.fsm.state import State, StatesGroup


class AddGame(StatesGroup):
    name = State()
    online_product = State()
    price_day = State()
    price_week = State()
    deposit = State()
    photo = State()
    price = State()
    finish = State()


class ChangeGame(StatesGroup):
    change_count = State()
    count = State()
    delete = State()


class DeleteAdmin(StatesGroup):
    delete_admin = State()


class ManageUser(StatesGroup):
    ban_user = State()
    unban_user = State()


class SetAvailable(StatesGroup):
    product_name = State()

