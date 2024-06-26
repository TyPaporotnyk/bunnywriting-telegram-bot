from aiogram.fsm.state import State, StatesGroup


class RegisterFormState(StatesGroup):
    get_first_name = State()
    get_last_name = State()
    get_card = State()
    get_specialities = State()


class MoneyState(StatesGroup):
    money = State()


class ChangeSpecialityState(StatesGroup):
    get_specialities = State()


class ChangeBussinessState(StatesGroup):
    get_bussines = State()
