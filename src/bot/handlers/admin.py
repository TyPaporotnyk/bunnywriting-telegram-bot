from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.filters.admin import IsAdmin
from src.bot.keyboards.admin import get_start_keyboard
from src.bot.states.admin import UserFormState, MailingFormState
from src.db.services.user import create_base_author
from src.db.services.admin import get_admin_author_ids

router = Router(name="admin")


@router.message(Command(commands="start2"), IsAdmin())
async def admin_start(message: types.Message):
    await message.answer("Ласкаво просимо, Адмін!", reply_markup=get_start_keyboard().as_markup())


@router.message(Command(commands="help2"), IsAdmin())
async def admin_help(message: types.Message):
    await message.answer("This message isanswear on the message above")


@router.callback_query(F.data == "add_author", IsAdmin())
async def add_author(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserFormState.user_data)
    await callback.message.answer("Надішліть дані автора автора в такому форматі\n'(айді-телеграм),(айді),(ім'я) (прізвище),(рейтинг)'")


@router.message(UserFormState.user_data)
async def get_author_name(message: types.Message, state: FSMContext, session):
    admin_id = message.from_user.id
    telegram_id, author_id, full_name, raiting = message.text.split(",")
    await create_base_author(session, {
        "id": telegram_id,
        "full_name": full_name,
        "raiting": raiting,
        "admin_id": admin_id
    })

    await message.answer("Автор був доданий")

    await state.clear()


@router.callback_query(F.data == "mailing", IsAdmin())
async def add_author(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Відправте повідомлення, яке ви хочете розіслати користувачам")
    await state.set_state(MailingFormState.message)


@router.message(MailingFormState.message)
async def add_author(message: types.Message, state: FSMContext, session):
    send_message = message.text
    admin_id = message.from_user.id

    authors_ids = await get_admin_author_ids(session, admin_id)

    if not authors_ids:
        await message.answer("У вашому підпорядкуванні немає жодного автора")


    # else:


    await state.clear()
