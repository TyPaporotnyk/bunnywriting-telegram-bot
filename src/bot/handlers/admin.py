from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.admin import IsAdmin
from src.bot.keyboards.admin import get_start_keyboard
from src.bot.states.admin import MailingFormState, UserFormState
from src.crm.author import Author
from src.crm.exceptions import AuthorNotCreated
from src.db import Lead
from src.db.services.admin import get_admin_author_ids, get_admin_authors
from src.db.services.author import create_base_author
from src.db.services.lead import (
    get_author_payment_list,
    get_current_author_payments,
    get_current_author_tasks,
    get_urgent_list,
)
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
    """
    Show all payment of an author
    """
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
    """
    Show deadline lead list of authors
    """
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
            leads_message += f"{author_task.id} - {author_task.deadline_for_author} - {author_task.status}\n"

        await callback.message.answer(leads_message)


def get_typed_leads(leads: list[Lead]) -> dict[str, list[Lead]]:
    urgent_list_typed = {}
    for urgent in leads:
        if urgent.status not in urgent_list_typed:
            urgent_list_typed[urgent.status] = []

        urgent_list_typed[urgent.status].append(urgent)

    return urgent_list_typed


@router.callback_query(F.data == "urgent_list", IsAdmin())
async def show_urgent_list(callback: types.CallbackQuery, session):
    """
    Show the urgent list of the authors
    """
    admin_id = callback.from_user.id
    urgent_list = await get_urgent_list(session, admin_id)

    urgent_list_typed = get_typed_leads(urgent_list)

    for urgent_status in urgent_list_typed:
        message = ""

        for urgent in urgent_list_typed[urgent_status]:
            message += (
                f"{urgent.id}; {urgent.deadline_for_author.strftime('%Y-%m-%d')};"
                f" {urgent.author_id} - {urgent.status}\n"
            )

        await callback.message.answer(message)


@router.callback_query(F.data == "payment_list", IsAdmin())
async def show_payment_list(callback: types.CallbackQuery, session):
    """
    Show the payment list of the authors
    """
    admin_id = callback.from_user.id
    authors = await get_admin_authors(session, admin_id)

    if not authors:
        await callback.answer("У вас немає жодного автора")
        return

    message = ""

    for author in authors:
        author_payment_leads = await get_author_payment_list(session, admin_id, author.custom_id)

        if not author_payment_leads:
            continue

        author_payment_sum = sum(
            [
                author_payment_lead.expenses
                for author_payment_lead in author_payment_leads
                if author_payment_lead.expenses is not None
            ]
        )
        message += f"{author.id}; {author.card_number}\n"
        message += f"Сума: {author_payment_sum} грн\n"
        message += "Перелік робіт:\n"

        for author_payment_lead in author_payment_leads:
            message += f"{author_payment_lead.id}; {author_payment_lead.expenses}; {author_payment_lead.status}\n"

        message += "-----------------\n"

    if message:
        await callback.message.answer(message)

    else:
        await callback.answer("У вас нема виплат для авторів")


@router.callback_query(F.data == "salary", IsAdmin())
async def admin_salary(callback: types.CallbackQuery, session):
    """
    Show the salary of the admin
    """
    await callback.message.answer("Сума: 0 грн")
