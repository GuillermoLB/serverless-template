import json
import logging
from typing import Any

from app.dependencies import get_settings
from app.flows.publishers import send_event_message

logger = logging.getLogger(__name__)

settings = get_settings()


def get_event_body_records(event):
    root_records = event["Records"]
    body_records = []
    for record in root_records:
        body_records.append(json.loads(record["body"]))
    return body_records


def handle_event_processing(event: dict, sqs: Any, s3: Any):
    """Receive events from S3 and mark them as UPLOADED"""
    logger.info("DOCUMENT FROM S3 RECEIVED")
    body_records = get_event_body_records(event)
    try:
        send_event_message(
            sqs=sqs,
            queue_url=settings.DOCUMENTS_TO_DETECT_QUEUE,
            delay=settings.DOCUMENTS_QUEUE_DELAY,
        )
    except Exception as e:  # TODO: fine-grain exception
        logger.error(e)
