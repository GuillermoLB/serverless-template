import logging
from typing import Any

logger = logging.getLogger(__name__)


def send_event_message(
    sqs: Any,
    queue_url: str,
    delay: int
):
    if queue_url:
        sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=delay,  # configure delay before sending to the Q
        )
        logger.info(f"Event message sent to '{queue_url}'")
    else:
        logger.info(
            f"Event message not sent because queue is not configured"
        )
