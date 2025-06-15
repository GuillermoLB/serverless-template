""" Handle incoming events to Lambda function and dispatch to services"""

import logging

from app.dependencies import get_s3, get_sqs_client
from app.flows.event_flow import handle_event_processing

logger = logging.getLogger(__name__)

sqs = get_sqs_client()
s3 = get_s3()


def get_sqs_event_source(event):
    records = event["Records"]
    return records[0]["eventSourceARN"].split(":")[-1] if records else None


def handle_sqs_event(event, context):
    logger.info(f"Received SQS Event: {event}")
    # Don't log API events, they may contain huge base64-encoded files in "body" field
    event_source = get_sqs_event_source(event)
    logger.info(f"SQS Event Source: {event_source}")
    # S3 files uploaded events
    if event_source == "EventToProcess":
        handle_event_processing(
            event=event, sqs=sqs, s3=s3)
