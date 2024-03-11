import asyncio
from datetime import datetime, timedelta

from loguru import logger

from src.bot.misc import bot
from src.db.database import session_maker
from src.db.services.author import get_author_by_telegram_id
from src.db.services.lead import get_leads_by_status, update_lead_com_alert, update_lead_priority

from src.bot.services.broadcaster import send_message


async def send_alert_message(bot, author, lead, message):
    await send_message(bot, author, f'Нагадування! До замовлення №{lead["id"]}, {message}')


async def process_leads(sesson, leads, status, hours_conditions, com_alert_values):
    for lead in leads:
        try:
            author = await get_author_by_telegram_id(crm_id=int(lead["author_id"]))
            if author is not None:
                now = datetime.now()
                time = datetime(
                    lead["deadline_for_author"].year,
                    lead["deadline_for_author"].month,
                    lead["deadline_for_author"].day,
                )

                for hours, com_alert_value in zip(hours_conditions, com_alert_values):
                    if now > (time - timedelta(hours=hours)):
                        await send_alert_message(bot, author, lead, com_alert_value)

                        if status == "План" and hours > 24 and lead["priority"] < 3:
                            await update_lead_priority(lead_id=lead["id"], priority=3)

                        if status != "План":
                            await update_lead_com_alert(lead_id=lead["id"], com_alert=com_alert_value)

                        break

        except Exception as e:
            logger.warning(f"Ошибка отправки напоминания. Статус: {status}, Lead ID: {lead['id']}")
    await asyncio.sleep(43200)


async def alert_scheduler():
    async with session_maker() as session:
        leads_plan = await get_leads_by_status("План")
        await process_leads(session, leads_plan, "План", [24, 36, 48], ["12h", "12h", "24h"])

        leads_in_progress = await get_leads_by_status("В роботі")
        await process_leads(session, leads_in_progress, "В роботі", [12, 24, 48, 72, 120], ["12h", "24h", "48h", "72h", "120h"])

        leads_corrections = await get_leads_by_status("Правки в роботі")
        await process_leads(
            session, leads_corrections, "Правки в роботі", [12, 24, 48, 72, 120], ["12h", "24h", "48h", "72h", "120h"]
        )


async def main():
    asyncio.create_task(alert_scheduler())


if __name__ == "__main__":
    asyncio.run(main())
