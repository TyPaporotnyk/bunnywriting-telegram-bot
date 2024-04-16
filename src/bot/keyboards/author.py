from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder


def get_start_keyboard():
    help_buttons = InlineKeyboardBuilder()
    help_buttons.add(InlineKeyboardButton(text="📚Актуальне", callback_data="current_tasks"))
    help_buttons.add(InlineKeyboardButton(text="💰Виплати", callback_data="author_payment"))
    help_buttons.add(InlineKeyboardButton(text="🎓Змінити спеціальності", callback_data="change_specialities"))
    help_buttons.add(InlineKeyboardButton(text="🛠Змінити планову навантаженість", callback_data="change_busyness"))
    help_buttons.add(
        InlineKeyboardButton(text="💥Список термінових", callback_data="author_urgent_list"),
    )
    help_buttons.adjust(1)
    return help_buttons


def lead_answer():
    home_buttons = ReplyKeyboardBuilder()
    home_buttons.add(types.KeyboardButton(text="✅Прийняти"))
    home_buttons.add(types.KeyboardButton(text="❌Відхилити"))
    home_buttons.adjust(2)
    return home_buttons


def lead_auction_answer():
    home_buttons = ReplyKeyboardBuilder()
    home_buttons.add(types.KeyboardButton(text="✅Прийняти замовлення"))
    home_buttons.add(types.KeyboardButton(text="❌Відхилити"))
    home_buttons.adjust(2)
    return home_buttons


def answer_speciality(specialities):
    home_buttons = ReplyKeyboardBuilder()
    home_buttons.row(types.KeyboardButton(text="Готово✅"))

    for value in specialities:
        home_buttons.add(types.KeyboardButton(text=value))

    home_buttons.adjust(2)
    return home_buttons


def mailing_buttons(lead_id: int, lead_type: str):
    home_buttons = InlineKeyboardBuilder()
    home_buttons.add(InlineKeyboardButton(text="✅Прийняти", callback_data=f"accept-{lead_id}-{lead_type}"))
    home_buttons.add(InlineKeyboardButton(text="❌Відхилити", callback_data=f"refuce-{lead_id}-{lead_type}"))
    home_buttons.adjust(2)
    return home_buttons
