from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_start_keyboard():
    help_buttons = InlineKeyboardBuilder()

    help_buttons.row(InlineKeyboardButton(text="📰Розсилка", callback_data="mailing"))
    help_buttons.row(InlineKeyboardButton(text="➕Додати автора", callback_data="add_author"))
    help_buttons.row(InlineKeyboardButton(text="💸Виплати", callback_data="author_payouts"))
    help_buttons.row(InlineKeyboardButton(text="⏰Дедлайни", callback_data="author_deadlines"))

    return help_buttons
