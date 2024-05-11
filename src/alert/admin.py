from loguru import logger

from src.bot.misc import bot
from src.bot.services.broadcaster import send_message
from src.db import Lead, session_maker
from src.db.services.lead import get_overdue_works


def group_overdue_works_by_team_lead(leads: list[Lead]) -> dict[int, list[Lead]]:
    grouped_leads: dict[int, list[Lead]] = {}

    for lead in leads:
        if lead.team_lead not in grouped_leads:
            grouped_leads[lead.team_lead] = []

        grouped_leads[lead.team_lead].append(lead)

    return grouped_leads


def get_team_lead_alert_message(leads: list[Lead]) -> str:
    message = "⚠️Нагадування до замовлень⚠️\n"

    for lead in leads:
        message += f"{lead.id}, {lead.real_deadline.strftime('%Y-%m-%d')}\n"

    return message


async def send_team_lead_alerts(team_lead: int, leads: list[Lead]):
    message = get_team_lead_alert_message(leads)

    await send_message(bot, team_lead, message)
    logger.info(f"Alert has been sent to {team_lead} team lead")


async def send_team_leads_alerts():
    logger.info("Sending admin alerts")
    async with session_maker() as session:
        overdue_works = await get_overdue_works(session)
        grouped_overdue_leads = group_overdue_works_by_team_lead(overdue_works)

    for team_lead in grouped_overdue_leads:
        team_lead_leads = grouped_overdue_leads[team_lead]
        await send_team_lead_alerts(team_lead, team_lead_leads)
