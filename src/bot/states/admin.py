from aiogram.fsm.state import State, StatesGroup


class UserFormState(StatesGroup):
    user_data = State()


class MailingFormState(StatesGroup):
    message = State()
