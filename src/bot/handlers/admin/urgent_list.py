from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.admin import IsAdmin
from src.bot.states.admin import UrgentStates
from src.db import Lead
from src.db.services.lead import get_urgent_list

router = Router(name="admin_urgent_list")


def get_typed_leads(leads: list[Lead]) -> dict[str, list[Lead]]:
    urgent_list_typed = {}
    for urgent in leads:
        if urgent.status not in urgent_list_typed:
            urgent_list_typed[urgent.status] = []

        urgent_list_typed[urgent.status].append(urgent)

    return urgent_list_typed


@router.callback_query(F.data == "urgent_list", IsAdmin())
async def show_urgent_list_by_author_id(callback: types.CallbackQuery, session):
    """
    Show the urgent list of the authors
    """
    admin_id = callback.from_user.id
    urgent_list = await get_urgent_list(session, admin_id)

    logger.info("Test")

    if not urgent_list:
        await callback.answer("У вас нема списку термінових робіт")

    urgent_list_typed = get_typed_leads(urgent_list)

    for urgent_status in urgent_list_typed:
        message_template = f"Список термінових робіт за статусом {urgent_status}:\n"

        for urgent in urgent_list_typed[urgent_status]:
            message_template += f"{urgent.id}; {urgent.deadline_for_author.strftime('%m-%d')}\n"

        await callback.message.answer(message_template)


@router.callback_query(F.data == "urgent_list_by_author", IsAdmin())
async def get_author_id_for_urgent_list(callback: types.CallbackQuery, state: FSMContext):
    """
    Enter author id to get them urgent list
    """
    await callback.message.answer(
        "Напишіть айді автора список термінових робіт якого хочете подивитись або Вийти для скасування дії"
    )
    await state.set_state(UrgentStates.get_author_id)


@router.message(F.text.func(lambda s: "вийти" in str(s).lower()), UrgentStates.get_author_id)
async def exit_author_id_for_urgent_list(message: types.Message, state: FSMContext):
    await message.reply("Дякую за відповідь", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.func(lambda s: not str(s).isdigit()), UrgentStates.get_author_id)
async def wrong_author_id_for_urgent_list(message: types.Message):
    await message.reply(
        "Введіть правильний айді автора (ціле число) або Вийти для скасування дії",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(F.text, UrgentStates.get_author_id)
async def show_urgent_list(message: types.Message, state: FSMContext, session):
    """
    Show the urgent list of the authors
    """
    admin_id = message.from_user.id
    author_id = int(message.text)
    urgent_list = await get_urgent_list(session, admin_id, author_id)

    if not urgent_list:
        await message.answer("Даний автор не має списку термінових завдань")

    urgent_list_typed = get_typed_leads(urgent_list)

    for urgent_status in urgent_list_typed:
        message_template = f"Список термінових робіт за статусом {urgent_status} автора {author_id}:\n"

        for urgent in urgent_list_typed[urgent_status]:
            message_template += f"{urgent.id}; {urgent.deadline_for_author.strftime('%m-%d')}\n"

        await message.answer(message_template)

    await state.clear()
