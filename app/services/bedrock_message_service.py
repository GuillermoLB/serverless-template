from dataclasses import dataclass
import datetime
import uuid
from app.schemas.bedrock_message_schemas import BedrockMessage, BedrockMessageCreate, BedrockMessageLog, BedrockMessageStore, BedrockMessagesRead


from sqlalchemy.orm import Session
import logging
from typing import Dict, Any, Optional, List
import json

from app.schemas.bedrock_response_schemas import BedrockResponse
from app.services import bedrock_response_service
from functools import partial

logger = logging.getLogger(__name__)



def store_message_text(
    session_id: str,
    invocation_id: str,
    message_text: str,
    bedrock: any
) -> None:
    # Skip storing empty strings
    if not message_text or message_text.strip() == "":
        logger.warning("Skipping storage of empty message text")
        return
        
    bedrock.put_invocation_step(
        invocationIdentifier=invocation_id,
        invocationStepId=str(uuid.uuid4()),
        invocationStepTime=datetime.datetime.now(),
        sessionIdentifier=session_id,
        payload={
            'contentBlocks': [
                {
                    'text': message_text,
                }            
            ]
        },
    )

def store_message(
    message_store: BedrockMessageStore,
    bedrock: any,
) -> BedrockMessage:
    """
    Store the message in the Bedrock agent.
    """
    logger.info(f"Storing message with query: {message_store.query}")

    # Create a partial function for convenience
    store_message_text_partial = partial(
        store_message_text,
        bedrock=bedrock,
        session_id=message_store.session_id,
        invocation_id=message_store.invocation_id,
    )
    
    # Store the query (if not empty)
    if message_store.query and message_store.query.strip():
        store_message_text_partial(message_text=message_store.query)
    
    # Store the response text (if not empty)
    if message_store.response_text and message_store.response_text.strip():
        store_message_text_partial(message_text=message_store.response_text)
    
    # Store citations separately (if there are any)
    if message_store.citations and len(message_store.citations) > 0:
        citations_text = "Citations:\n"
        for citation in message_store.citations:
            if citation and citation.strip():
                citations_text += f"- {citation}\n"
        
        # Only store citations if there are actually any non-empty ones
        if citations_text != "Citations:\n":
            store_message_text_partial(message_text=citations_text)

    message = BedrockMessage(
        invocation_id=message_store.invocation_id,
        query=message_store.query,
        response_text=message_store.response_text,
        citations=message_store.citations
    )

    return message

def create_message(
    message_create: BedrockMessageCreate,
    bedrock: any,
) -> BedrockMessage:
    """
    Create a new message using the Bedrock agent.
    """
    logger.info(f"Creating message with query: {message_create.query}")

    invocation = bedrock.create_invocation(
        description="Message",
        sessionIdentifier=message_create.session_id
    )
    invocation_id = invocation["invocationId"]

    response = bedrock_response_service.create_response(
        response_create=message_create,
        bedrock=bedrock
    )
    
    # Create MessageStore directly with the response text and citations
    message_store = BedrockMessageStore(
        session_id=message_create.session_id,
        invocation_id=invocation_id,
        query=message_create.query,
        response_text=response.response_text,
        citations=response.citations
    )

    message = store_message(
        message_store=message_store,
        bedrock=bedrock
    )

    logger.info(f"Created message with query length: {len(message.query)}, response length: {len(message.response_text)}")
    
    return message

def get_session_messages(
    bedrock: any,
    messages_read: BedrockMessagesRead
) -> List[BedrockMessage]:
    """
    Get all the responses for a given session.
    """
    logger.info(f"Reading messages for session: {messages_read.session_id}")

    session_id = messages_read.session_id
    invocations_response = bedrock.list_invocations(
        maxResults=messages_read.max_results,
        sessionIdentifier=session_id,
    )
    
    invocation_ids = []
    if 'invocationSummaries' in invocations_response:
        invocation_ids = [inv['invocationId'] for inv in invocations_response['invocationSummaries']]
    
    logger.info(f"Found {len(invocation_ids)} invocations for session {session_id}")
    messages = []
    
    # Process each invocation and build message list
    for invocation_id in invocation_ids:
        message = get_message(
            bedrock=bedrock,
            session_id=session_id,
            invocation_id=invocation_id
        )
        
        if message:
            messages.append(message)
    
    return messages

def get_message(
    bedrock: any,
    session_id: str,
    invocation_id: str
) -> Optional[BedrockMessage]:
    """
    Get a specific message by its invocation ID.
    
    Args:
        bedrock: AWS Bedrock client
        session_id: The session identifier
        invocation_id: The specific invocation identifier to retrieve
        
    Returns:
        Message object if found, None otherwise
    """
    logger.info(f"Reading message with invocation ID: {invocation_id} from session: {session_id}")
    
    try:
        invocation_steps_response = bedrock.list_invocation_steps(
            invocationIdentifier=invocation_id,
            sessionIdentifier=session_id,
        )
        
        if 'invocationStepSummaries' not in invocation_steps_response or not invocation_steps_response['invocationStepSummaries']:
            logger.warning(f"No steps found for invocation {invocation_id}")
            return None
            
        # Get all steps for this invocation
        steps = sorted(
            invocation_steps_response['invocationStepSummaries'], 
            key=lambda x: x['invocationStepTime']
        )
        
        # Container for our message parts
        query_text = None
        response_text = None
        citations = []
        
        # Process steps based on content patterns
        for i, step in enumerate(steps):
            try:
                step_detail = bedrock.get_invocation_step(
                    invocationIdentifier=invocation_id,
                    invocationStepId=step['invocationStepId'],
                    sessionIdentifier=session_id,
                )
                
                if 'invocationStep' not in step_detail or 'payload' not in step_detail['invocationStep']:
                    continue
                    
                payload = step_detail['invocationStep']['payload']
                if 'contentBlocks' not in payload or not payload['contentBlocks']:
                    continue
                    
                content_text = payload['contentBlocks'][0].get('text', '')
                
                # Identify content type by patterns
                if content_text.startswith("Citations:"):
                    # Extract citations from the text
                    citation_lines = content_text.strip().split("\n")[1:]  # Skip the "Citations:" line
                    citations = [line[2:].strip() if line.startswith("- ") else line.strip() 
                                for line in citation_lines if line.strip()]
                elif i == 0 and not content_text.startswith("Citations:"):
                    # First non-citation content is usually the query
                    query_text = content_text
                elif query_text and not response_text and not content_text.startswith("Citations:"):
                    # First content after query that's not citations is usually the response
                    response_text = content_text
                
            except Exception as e:
                logger.error(f"Error processing step {step['invocationStepId']}: {str(e)}")
        
        # Clean up response text if needed (sometimes query may be appended)
        if response_text and query_text and response_text.endswith(query_text):
            response_text = response_text[:-len(query_text)].strip()
        
        # Create message only if we have both query and response
        if query_text and response_text:
            return BedrockMessage(
                session_id=session_id,
                invocation_id=invocation_id,
                query=query_text,
                response_text=response_text,
                citations=citations
            )
        else:
            logger.warning(f"Could not extract complete message for invocation {invocation_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error processing invocation {invocation_id}: {str(e)}")
        return None

def log_message(
    message_log: BedrockMessageLog,
    cloudwatch: any,
    bedrock:any,
) -> None:
    """
    Log a message to the Bedrock agent.
    """

    message = get_message(
        bedrock=bedrock,
        session_id=message_log.session_id,
        invocation_id=message_log.invocation_id
    )

    logger.info(f"Logging message with feedback: {message_log.feedback}")

    # Obtener información sobre el log stream  
    response = cloudwatch.describe_log_streams(
        logGroupName=message_log.log_group_name,
        logStreamNamePrefix=message_log.log_stream_name
    )

    log_streams = response.get("logStreams", [])
    sequence_token = log_streams[0].get("uploadSequenceToken") # Sequence token necesario para el log

    log_event = {
        "logGroupName": message_log.log_group_name,
        "logStreamName": message_log.log_stream_name,
        "logEvents": [
            {
                "timestamp": int(datetime.datetime.now().timestamp() * 1000),  # Fixed line
                "message": f"""\n
                ======= FEEDBACK INFORMATION ======= \n
                User ID: {message_log.user_id}\n
                Feedback: {message_log.feedback}\n

                ======= SESSION DETAILS =======\n
                Session ID: {message_log.session_id}\n
                Invocation ID: {message.invocation_id}\n
                ======= CONVERSATION =======\n
                Query: \n
                {message.query}\n

                Response:\n
                {message.response_text}\n
                """
            }
        ]
    }

    if sequence_token:
        log_event["sequenceToken"] = sequence_token

    # Enviar evento a CloudWatch
    cloudwatch.put_log_events(**log_event)






