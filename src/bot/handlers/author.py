from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.bot.filters.user import IsAuthor, IsNotRegisteredAuthor
from src.bot.keyboards.author import answer_speciality, get_start_keyboard
from src.bot.services.redis import get_public_auction_answer, set_public_auction_answer
from src.bot.states.author import ChangeBussinessState, ChangeSpecialityState, MoneyState, RgisterFormState
from src.crm.author import Author
from src.db.services.author import (
    db_register_author,
    get_author_by_telegram_id,
    update_author_plane_busyness,
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
        logger.error(f"Cant to update plane busyness: {repr(e)}")
    else:
        await message.answer(
            "Вітаю! 🥳 Спеціальності були змінені!",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    await state.clear()


@router.callback_query(F.data == "change_busyness", IsAuthor())
async def change_busyness(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Вкажи бажане планове навантаження не більше 20",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(ChangeBussinessState.get_bussines)


@router.message(F.text.func(lambda message: not message.isdigit()), ChangeBussinessState.get_bussines)
async def action_change_busyness(message: types.Message):
    await message.reply("Введіть правильне, ціле число")


@router.message(F.text, ChangeBussinessState.get_bussines)
async def change_plane_busyness(message: types.Message, state: FSMContext, session):
    author_id = message.from_user.id
    plane_busyness = int(message.text)

    if plane_busyness >= 20:
        await message.reply("Введіть число яке не більше за 20")
        return

    author = await get_author_by_telegram_id(session, author_id)

    try:
        await Author.update_author_busyness_and_open_leads(author.id, plane_busyness, author.open_leads)
        await update_author_plane_busyness(session, author.telegram_id, plane_busyness)
    except Exception as e:
        await message.answer("Планова навантаженість не була змінена", reply_markup=types.ReplyKeyboardRemove())
        logger.error(f"Cant to update plane busyness: {repr(e)}")
    else:
        await message.answer("Планова навантаженість була успішно змінена", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()


@router.callback_query(F.data.func(lambda c: "public" in c))
async def author_public_auction(callback: types.CallbackQuery):
    answer, lead_id, lead_type = callback.data.split("-")
    author_id = callback.from_user.id

    if (await get_public_auction_answer(lead_id, author_id)) == "wait":
        await set_public_auction_answer(lead_id, author_id, answer)

        if answer == "accept":
            await callback.message.answer(
                f"Чудово, замовлення №{lead_id} твоє!",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            logger.info(f"Автор {author_id} принял задание {lead_id}")
        elif answer == "refuce":
            await callback.message.answer("Дякую за в відповідь", reply_markup=types.ReplyKeyboardRemove())
            logger.info(f"Автор [{author_id}] отказался от задания {lead_id}")
    else:
        await callback.answer("Замовлення не активне")

    await callback.message.edit_reply_markup(reply_markup=None)


@router.callback_query(F.data.func(lambda c: "private" in c))
async def admin_start(callback: types.CallbackQuery, state: FSMContext):
    answer, lead_id, lead_type = callback.data.split("-")
    author_id = callback.from_user.id

    if (await get_public_auction_answer(lead_id, author_id)) == "wait":
        if answer == "accept":
            await callback.message.answer(
                '👇Вкажи свою ставку (лише число, без "грн")',
                reply_markup=types.ReplyKeyboardRemove(),
            )
            logger.info(f"Автор [{callback.from_user.id}] принял участие в аукционе")
            await state.update_data(lead_id=lead_id)
            await state.set_state(MoneyState.money)
        else:
            await callback.message.answer("Дякую за в відповідь", reply_markup=types.ReplyKeyboardRemove())
            logger.info(f"Автор {author_id} отказался от приватного задания {lead_id}")
    else:
        await callback.answer("Замовлення не активне")

    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(F.text.func(lambda s: "вийти" in s.lower()), MoneyState.money)
async def test_start(message: types.Message, state: FSMContext):
    message.reply("Дякую за відповідь", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(F.text.func(lambda s: not s.isdigit()), MoneyState.money)
async def test_start(message: types.Message):
    await message.reply("Введіть правильне число, або 'Вийти' для відмови від участі в аукціоні")


@router.message(F.text, MoneyState.money)
async def test_start(message: types.Message, state: FSMContext):
    data = await state.get_data()
    author_id = message.from_user.id
    lead_id = data["lead_id"]
    price = message.text

    await set_public_auction_answer(lead_id, author_id, price)

    logger.info(f'Автор {message.from_user.id} вытсавил цену {message.text} за задание {data["lead_id"]}')
    await message.reply("⚖️Ставку прийнято! Ти отримаєш сповіщення, якщо твоя ставка виграє.")
    await state.clear()
