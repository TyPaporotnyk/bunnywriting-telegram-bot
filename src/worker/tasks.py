import logging

from src.worker.celery import app, celery_event_loop

logger = logging.getLogger(__name__)


@app.task
def test_task() -> None:
    logger.info("Test Message")
