from aiogram import F, Router, types
from aiogram.filters import Command

from src.bot.filters.admin import IsAdmin
from src.bot.keyboards.admin import get_start_keyboard
from src.db.services.admin import get_admin_authors
from src.db.services.lead import (
    get_admin_salary,
    get_author_payment_list,
    get_current_author_payments,
    get_current_author_tasks,
)

router = Router(name="admin_base")


@router.message(Command(commands="start2"), IsAdmin())
async def admin_start(message: types.Message):
    await message.answer("Ласкаво просимо, Адмін!", reply_markup=get_start_keyboard().as_markup())


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
                (
                    author_payment_lead.expenses
                    if author_payment_lead.expenses_status in [0, None]
                    else author_payment_lead.expenses / 2
                )
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
        msgs = [message[i : i + 4096] for i in range(0, len(message), 4096)]
        for text in msgs:
            await callback.message.answer(text)

    else:
        await callback.answer("У вас нема виплат для авторів")


@router.callback_query(F.data == "salary", IsAdmin())
async def admin_salary(callback: types.CallbackQuery, session):
    """
    Show the salary of the admin
    """
    admin_id = callback.from_user.id
    salary_leads = await get_admin_salary(session, admin_id)
    work_type_price = {
        "Курсова": 100,
        "Дипломна": 150,
        "Магістерська": 200,
    }
    salary_sum = 2500 + sum([work_type_price.get(salary_lead.work_type, 100) for salary_lead in salary_leads])
    await callback.message.answer(f"Сума: {salary_sum} грн")
