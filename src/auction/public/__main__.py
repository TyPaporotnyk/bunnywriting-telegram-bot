import asyncio
from datetime import datetime, time, timedelta

from loguru import logger

from src.auction.services import public_autction
from src.auction.utils import group_leads_by_work_type, update_lead_status
from src.bot.utils import logging
from src.crm.lead import Lead


async def find_auction_authors():
    logger.info("Начало поиска авторов на публичные проекты")

    leads = await Lead.get_leads_by_status(53018603)
    leads = list(filter(lambda x: x.speciality is not None, leads))
    logger.info(f"Получено {len(leads)} публичных проектов")
    if leads:
        grouped_leads = group_leads_by_work_type(leads)
        logger.info(f"Получено {len(leads)} публичных проектов сгруппированных по типу работы")

        tasks = [
            public_autction.find_authors(grouped_leads[work][0], delay) for delay, work in enumerate(grouped_leads)
        ]
        task_results = await asyncio.gather(*tasks)

        for task_result in task_results:
            is_finished_task = task_result[0]
            task_lead = task_result[1]
            if not is_finished_task:
                await update_lead_status(task_lead, 53018603, 53018607)
    else:
        logger.info("No new orders")


async def main():
    start_time = time(8, 0)
    end_time = time(22, 0)

    while True:
        now = (datetime.now() + timedelta(hours=4)).time()

        if start_time < now < end_time:
            await find_auction_authors()
        else:
            logger.info(f"Time is not reachable: {now}")
            await asyncio.sleep(3600)
            continue

        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.setup()
    asyncio.run(main())
