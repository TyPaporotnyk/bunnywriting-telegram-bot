from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.admin import IsAdmin
from src.bot.states.admin import MailingFormState
from src.db.services.admin import get_admin_author_ids
from src.worker import send_user_messages_task

router = Router(name="admin_mailing")


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
