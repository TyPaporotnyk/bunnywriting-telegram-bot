from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.user import IsAuthor, IsNotRegisteredAuthor
from src.bot.keyboards.author import answer_speciality, get_start_keyboard
from src.bot.states.author import ChangeBussinessState, ChangeSpecialityState, RgisterFormState
from src.crm.author import Author
from src.db.services.author import (
    db_register_author,
    get_author_by_telegram_id,
    update_author_busyness,
    update_author_specialities,
)
from src.db.services.lead import get_current_author_payments, get_current_author_tasks
from src.db.services.speciality import get_specialities

router = Router(name="commands")


@router.message(IsNotRegisteredAuthor(), CommandStart())
async def register_author(message: types.Message, state: FSMContext):
    await message.reply(
        "Привіт! 👋\nНадішли мені номер своєї карти, бажано приват універсальну (тільки не для виплат)💳"
    )
    await state.set_state(RgisterFormState.get_card)


@router.message(F.text, RgisterFormState.get_card)
async def admin_start(message: types.Message, state: FSMContext, session):
    await state.update_data(get_card=message.text)
    specialities = await get_specialities(session)
    await message.answer(
        'Чудово! 👍 Вкажи перелік спеціальностей, які тебе цікавлять та натисни кнопку "✅Готово"',
        reply_markup=answer_speciality(specialities).as_markup(resize_keyboard=True),
    )
    await state.set_state(RgisterFormState.get_specialities)


@router.message(RgisterFormState.get_specialities)
async def admin_start_register(message: types.Message, state: FSMContext, session):
    input_message = message.text
    author_id = message.from_user.id

    data = await state.get_data()
    specialities = data.get("get_specialities", [])

    if input_message != "Готово✅":
        specialities.append(input_message)
        await state.update_data(get_specialities=specialities)
        return

    card_number = data.get("get_card")
    author = await get_author_by_telegram_id(session, author_id)
    username = message.from_user.username
    telegram_url = f"https://t.me/{username}" if username else ""

    try:
        await Author.register_author(author.id, card_number, specialities, telegram_url)
        await db_register_author(session, author_id, card_number, specialities, telegram_url)
    except Exception as e:
        logger.error(f"Error when register authror: {repr(e)}")
        await message.answer(
            "Помилка реєстрації, звернись до свого менеджера", reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "Вітаю! 🥳 Реєстрація пройдена. Будь на готові, скоро будуть нові замовлення.🤩",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    await state.clear()


@router.message(IsAuthor(), CommandStart())
async def author_start(message: types.Message):
    await message.reply("Вітання!", reply_markup=get_start_keyboard().as_markup())


@router.callback_query(F.data == "current_tasks", IsAuthor())
async def get_current_tasks(callback: types.CallbackQuery, session):
    author_id = callback.from_user.id
    author = await get_author_by_telegram_id(session, author_id)
    author_tasks = await get_current_author_tasks(session, author.custom_id)

    if not author_tasks:
        await callback.answer("Немає активних замовлень")
        return

    for author_task in author_tasks:
        message = (
            f"🆔: {author_task.id}\n"
            f"📌**Статус**: {author_task.status}\n"
            f"◽️ **Пріоритет**:{author_task.priority}\n"
            f"◾️ Спеціальність: {author_task.speciality}\n"
            f"◽️ Вид роботи: {author_task.work_type}\n"
            f"◾️ Тема: {author_task.thema}\n"
            f"◽️ Обсяг: {author_task.pages} ст.\n"
            f"◾️ Унікальність: {author_task.uniqueness}\n"
            f"◽️ Дедлайн: {author_task.deadline_for_author}\n"
            f"◾️ Коментар: {author_task.note}\n"
            f"💸 Ціна: {author_task.sale}\n"
        )

        await callback.message.answer(message)


@router.callback_query(F.data == "author_payment", IsAuthor())
async def get_author_payment(callback: types.CallbackQuery, session):
    author_id = callback.from_user.id
    author = await get_author_by_telegram_id(session, author_id)
    author_payments = await get_current_author_payments(session, author.custom_id)

    if not author_payments:
        await callback.answer("Немає виплат")
        return

    sale_sum = 0
    leads_message = ""
    for author_payment in author_payments:
        sale_sum += author_payment.expenses
        leads_message += f"{author_payment.id} - {author_payment.expenses}\n"

    leads_message += f"\nСума: {sale_sum}"
    await callback.message.answer(leads_message)


@router.callback_query(F.data == "change_specialities", IsAuthor())
async def change_specialities(callback: types.CallbackQuery, state: FSMContext, session):
    specialities = await get_specialities(session)
    await callback.message.answer(
        'Вкажи перелік спеціальностей, які тебе цікавлять та натисни кнопку "✅Готово"',
        reply_markup=answer_speciality(specialities).as_markup(resize_keyboard=True),
    )
    await state.set_state(ChangeSpecialityState.get_specialities)


@router.message(F.text, ChangeSpecialityState.get_specialities)
async def get_author_specialities(message: types.Message, state: FSMContext, session):
    author_id = message.from_user.id
    input_message = message.text

    data = await state.get_data()
    specialities = data.get("get_specialities", [])

    if input_message != "Готово✅":
        specialities.append(input_message)
        await state.update_data(get_specialities=specialities)
        return

    author = await get_author_by_telegram_id(session, author_id)
    try:
        await Author.update_author_specialities(author.id, specialities)
        await update_author_specialities(session, author.telegram_id, specialities)
    except Exception as e:
        await message.answer(
            "Помилка в зміненні спеціальності!😢 \nЗвернись до свого менеджера",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        logger.error(f"Cant to update plane business: {repr(e)}")
    else:
        await message.answer(
            "Вітаю! 🥳 Спеціальності були змінені!",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    await state.clear()


@router.callback_query(F.data == "change_business", IsAuthor())
async def change_business(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вкажи бажане планове навантаження не більше 20",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(ChangeBussinessState.get_bussines)


@router.message(F.text.func(lambda message: not message.isdigit()), ChangeBussinessState.get_bussines)
async def action_change_business(message: types.Message):
    await message.reply("Введіть правильне, ціле число")


@router.message(F.text, ChangeBussinessState.get_bussines)
async def change_plane_business(message: types.Message, state: FSMContext, session):
    author_id = message.from_user.id
    plane_business = int(message.text)

    if plane_business >= 20:
        await message.reply("Введіть число яке не більше за 20")
        return

    author = await get_author_by_telegram_id(session, author_id)

    try:
        await Author.update_author_busyness(author.id, plane_business, author.open_leads)
        await update_author_busyness(session, author.telegram_id, plane_business)
    except Exception as e:
        await message.answer("Планова навантаженість не була змінена", reply_markup=types.ReplyKeyboardRemove())
        logger.error(f"Cant to update plane business: {repr(e)}")
    else:
        await message.answer("Планова навантаженість була успішно змінена", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()
