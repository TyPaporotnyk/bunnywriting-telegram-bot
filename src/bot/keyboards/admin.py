from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_start_keyboard():
    help_buttons = InlineKeyboardBuilder()

    help_buttons.row(InlineKeyboardButton(text="📰Розсилка авторам", callback_data="mailing"))
    help_buttons.row(InlineKeyboardButton(text="➕Додати автора", callback_data="add_author"))
    help_buttons.row(InlineKeyboardButton(text="💸Виплати авторам", callback_data="author_payments"))
    help_buttons.row(InlineKeyboardButton(text="⏰Дедлайни авторів", callback_data="author_deadlines"))

    return help_buttons
