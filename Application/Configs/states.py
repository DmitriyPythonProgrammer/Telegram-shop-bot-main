from aiogram.fsm.state import StatesGroup, State


class Input_Settings(StatesGroup):
    change = State()
    in_menu = State()

