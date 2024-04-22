from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def get_start_keyboard():
    help_buttons = InlineKeyboardBuilder()

    help_buttons.row(InlineKeyboardButton(text="📰Розсилка авторам", callback_data="mailing"))
    help_buttons.row(InlineKeyboardButton(text="➕Додати автора", callback_data="add_author"))
    help_buttons.row(
        # InlineKeyboardButton(text="💸Виплати авторам", callback_data="author_payments"),
        InlineKeyboardButton(text="💰Список виплат", callback_data="payment_list"),
    )
    help_buttons.row(InlineKeyboardButton(text="⏰Дедлайни авторів", callback_data="author_deadlines"))
    help_buttons.row(InlineKeyboardButton(text="💥Список термінових", callback_data="urgent_list"))
    help_buttons.row(
        InlineKeyboardButton(text="💥Список термінових за автором", callback_data="urgent_list_by_author")
    )

    help_buttons.row(InlineKeyboardButton(text="Місячна ЗП", callback_data="salary"))

    return help_buttons
