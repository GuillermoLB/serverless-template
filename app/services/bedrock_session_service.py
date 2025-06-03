from app.schemas.bedrock_session_schemas import BedrockSession, BedrockSessionCreate, BedrockSessionCreate, BedrockSessionDelete, BedrockSessionSummarized, BedrockSessionsRead

import logging
from typing import Dict, Any, Optional, List
import json

logger = logging.getLogger(__name__)


def create_session(bedrock: any, bedrock_session_create: BedrockSessionCreate) -> BedrockSession:

    session = bedrock.create_session(
        encryptionKeyArn=bedrock_session_create.encryption_key_arn
    )
    session_id = session["sessionId"]



    session = BedrockSession(
        session_id=session_id,
    )
    return session


def process_memory_response(
    response: Dict[str, Any]
) -> list[BedrockSessionSummarized]:
    """
    Process the memory response from the Bedrock API.
    Extract unique session IDs from the memoryContents.
    """
    # Log the full response for debugging
    logger.info(f"{response}")
    
    # Get the memory contents list from the response
    memory_contents = response.get('memoryContents', [])
    
    # Track unique session IDs
    unique_session_ids = set()
    result = []
    
    # Extract session IDs from each memory content item
    for memory_item in memory_contents:
        logger.info(f"Memory item: {memory_item}")
        if 'sessionSummary' in memory_item and 'sessionId' in memory_item['sessionSummary']:
            session_id = memory_item['sessionSummary']['sessionId']
            
            # Only add unique session IDs
            if session_id not in unique_session_ids:
                unique_session_ids.add(session_id)
                
                # Get the most recent session summary for this ID
                summary = memory_item['sessionSummary'].get('summaryText', '')
                
                # Create BedrockSession without expiry_time and start_time
                result.append(BedrockSessionSummarized(
                    session_id=session_id,
                    session_summary=summary
                ))
    
    return result


def get_user_sessions(
    bedrock: any,
    bedrock_sessions_read: BedrockSessionsRead,
) -> list[BedrockSessionSummarized]:
    memory_response = bedrock.get_agent_memory(
        agentId=bedrock_sessions_read.agent_id,
        agentAliasId=bedrock_sessions_read.agent_alias_id,
        maxItems=bedrock_sessions_read.max_items,
        memoryId=bedrock_sessions_read.memory_id,
        memoryType=bedrock_sessions_read.memory_type
    )
    logger.info(f"User: {bedrock_sessions_read.memory_id}")

    processed_memory_response = process_memory_response(
        response=memory_response
    )
    return processed_memory_response

def delete_session(
    bedrock: any,
    bedrock_session_delete: BedrockSessionDelete
) -> None:
    """
    Delete a session
    """

    bedrock_session_id = bedrock_session_delete.session_id

    # TODO: try catch exception if no session found

    logger.info(f"Terminating session: {bedrock_session_id}")
    bedrock.end_session(
        sessionIdentifier=bedrock_session_id
    )

    logger.info(f"Ending session: {bedrock_session_id}")
    bedrock.delete_session(
        sessionIdentifier=bedrock_session_id
    )
