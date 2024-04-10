from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.admin import IsAdmin
from src.bot.keyboards.admin import get_start_keyboard
from src.bot.states.admin import MailingFormState, UserFormState
from src.crm.author import Author
from src.crm.exceptions import AuthorNotCreated
from src.db.services.admin import get_admin_author_ids, get_admin_authors
from src.db.services.author import create_base_author
from src.db.services.lead import get_current_author_payments, get_current_author_tasks, get_urgent_list
from src.worker import send_user_messages_task

router = Router(name="admin")


@router.message(Command(commands="start2"), IsAdmin())
async def admin_start(message: types.Message):
    await message.answer("Ласкаво просимо, Адмін!", reply_markup=get_start_keyboard().as_markup())


@router.callback_query(F.data == "add_author", IsAdmin())
async def add_author(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserFormState.user_data)
    await callback.message.answer(
        "Надішліть дані автора автора в такому форматі\n'(айді-телеграм),(айді),(ім'я) (прізвище),(рейтинг)'"
    )


@router.message(UserFormState.user_data)
async def get_author_name(message: types.Message, state: FSMContext, session):
    admin_id = message.from_user.id

    try:
        telegram_id, author_id, full_name, rating = list(map(str.strip, message.text.split(",")))

        await Author.create_author(telegram_id, author_id, full_name, rating, admin_id)
        await create_base_author(
            session, {"id": telegram_id, "name": full_name, "rating": rating, "admin_id": admin_id}
        )

        await message.answer("✅Автор був доданий")
    except AuthorNotCreated:
        await message.answer("❌Автор не був доданий")
    except Exception as e:
        await message.answer("❌Автор не був доданий")
        logger.error(f"Author has not been created by not raized error: {repr(e)}")

    await state.clear()


@router.callback_query(F.data == "mailing", IsAdmin())
async def admin_mailing(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Відправте повідомлення, яке ви хочете розіслати користувачам")
    await state.set_state(MailingFormState.message)


@router.message(MailingFormState.message)
async def admin_mailing_message(message: types.Message, state: FSMContext, session):
    send_message = message.text
    admin_id = message.from_user.id

    authors_ids = await get_admin_author_ids(session, admin_id)

    if not authors_ids:
        await message.answer("У вашому підпорядкуванні немає жодного автора")

    else:
        try:
            send_user_messages_task.delay(authors_ids, send_message)
        except Exception as e:
            logger.error(f"Send user messages task has not been created successfully: {repr(e)}")
            await message.answer("❌Сталася помилка при створенні завдання на розсилку")
        else:
            await message.answer("✅Завдання розсилки повідомлень було успішно створено")

    await state.clear()


@router.callback_query(F.data == "author_payments", IsAdmin())
async def author_payments(callback: types.CallbackQuery, session):
    admin_id = callback.from_user.id
    authors = await get_admin_authors(session, admin_id)

    if not authors:
        await callback.answer("У вас немає жодного автора")
        return

    for author in authors:
        author_payments = await get_current_author_payments(session, author.custom_id)

        if not author_payments:
            continue

        sale_sum = 0
        leads_message = f"Автор: {author.custom_id}, {author.name}, {author.card_number}\n"
        for author_payment in author_payments:
            sale_sum += author_payment.expenses
            leads_message += f"{author_payment.id} - {author_payment.expenses}\n"

        leads_message += f"Сума: {sale_sum}\n\n"
        await callback.message.answer(leads_message)


@router.callback_query(F.data == "author_deadlines", IsAdmin())
async def author_deadlines(callback: types.CallbackQuery, session):
    admin_id = callback.from_user.id
    authors = await get_admin_authors(session, admin_id)

    if not authors:
        await callback.answer("У вас немає жодного автора")
        return

    for author in authors:
        author_tasks = await get_current_author_tasks(session, author.custom_id)

        if not author_tasks:
            continue

        leads_message = f"Автор: {author.custom_id}, {author.name}\n"
        for author_task in author_tasks:
            leads_message += f"{author_task.id} - {author_task.real_deadline} - {author_task.status}\n"

        await callback.message.answer(leads_message)


@router.callback_query(F.data == "urgent_list", IsAdmin())
async def show_urgent_list(callback: types.CallbackQuery, session):
    """
    Show the urgent list of the authors
    """
    admin_id = callback.from_user.id
    urgent_list = await get_urgent_list(session, admin_id)

    message = ""
    for urgent in urgent_list:
        message += f"{urgent.id}; {urgent.deadline_for_author}; {urgent.author_id}\n"

    await callback.message.answer(message)
