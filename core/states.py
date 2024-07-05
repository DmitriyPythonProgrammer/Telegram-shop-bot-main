from aiogram.fsm.state import StatesGroup, State


class Address(StatesGroup):
    address = State()


class Suggestion(StatesGroup):
    suggestion = State()


class Ask(StatesGroup):
    question = State()


class Shop(StatesGroup):
    pickup_method = State()
    pay = State()
    payment = State()
    finish = State()
    delete = State()
    add = State()
    choose = State()
    buy_or_arend = State()
    count = State()
