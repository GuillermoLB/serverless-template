from http.client import HTTPException
import logging
from fastapi import APIRouter
from app.dependencies import BedrockDep, CloudwatchDep, SettingsDep, UserDep
from app.schemas.bedrock_message_schemas import BedrockMessage, BedrockMessageCreate, BedrockMessageFeedbackType, BedrockMessageLog, BedrockMessagesRead, BedrockQuery
from app.schemas.bedrock_session_schemas import BedrockSession, BedrockSessionCreate, BedrockSessionSummarized, BedrockSessionsRead
from app.services import bedrock_message_service, bedrock_session_service

copilot_router = APIRouter(prefix="/api/copilot/sessions", tags=["Copiloto IA"])



logger = logging.getLogger(__name__)


@copilot_router.post("/", response_model=BedrockSession) # Create a new session
async def create_session(
    bedrock: BedrockDep,
    settings: SettingsDep,
    current_user: UserDep,
):
    """
    Create a new session
    """
    try:
        logger.info(f"Creating session for user: {current_user.id}")

        bedrock_session_create = BedrockSessionCreate(
            encryption_key_arn=settings.ENCRIPTION_KEY_ARN,
        )
        
        created_session = bedrock_session_service.create_session(
            bedrock=bedrock,
            bedrock_session_create=bedrock_session_create
        )
        return created_session
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)


@copilot_router.get("/", response_model=list[BedrockSessionSummarized])
async def get_sessions(
    bedrock: BedrockDep,
    settings: SettingsDep,
    current_user: UserDep,
):
    """
    Get the user sessions
    """
    try:
        bedrock_sessions_read = BedrockSessionsRead(
            agent_id=settings.AGENT_ID,
            agent_alias_id=settings.AGENT_ALIAS_ID,
            max_items=settings.MEMORY_MAX_ITEMS,
            memory_id=str(current_user.id),
            memory_type=settings.MEMORY_TYPE
        )

        user_sessions = bedrock_session_service.get_user_sessions(
            bedrock=bedrock,
            bedrock_sessions_read=bedrock_sessions_read
        )
        return user_sessions
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)



@copilot_router.post("/{session_id}/messages", response_model=BedrockMessage) # Create a new response
async def create_message(
    bedrock: BedrockDep,
    settings: SettingsDep,
    current_user: UserDep,
    session_id: str,
    query: BedrockQuery
):
    """
    Generate a message for a given session and query.
    """
    try:
        logger.info(f"Generating text for prompt: {query}")
        message_create = BedrockMessageCreate(
            agent_id=settings.AGENT_ID,
            agent_alias_id=settings.AGENT_ALIAS_ID,
            memory_id=str(current_user.id),
            session_id=session_id,
            session_state=settings.get_session_state(),
            query=query.query_text,
        )

        return bedrock_message_service.create_message(
            message_create=message_create,
            bedrock=bedrock
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)


@copilot_router.get("/{session_id}/messages", response_model=list[BedrockMessage])
async def get_messages(
    settings: SettingsDep,
    bedrock: BedrockDep,
    session_id: str,
    current_user: UserDep,
):
    """
    Retrieve messages for a given session.
    """
    try:
        logger.info(f"Retrieving messages for session: {session_id}")

        bedrock_messages_read = BedrockMessagesRead(
            session_id=session_id,
            max_results=settings.MESSAGES_MAX_RESULTS,
        )
        messages = bedrock_message_service.get_session_messages(
            bedrock=bedrock,
            messages_read=bedrock_messages_read
        )

        return messages
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)


@copilot_router.post("/{session_id}/messages/{invocation_id}/like") # Create a new response
async def like_message(
    bedrock: BedrockDep,
    cloudwatch: CloudwatchDep,
    settings: SettingsDep,
    current_user: UserDep,
    session_id: str,
    invocation_id: str,
):
    """
    Like a message for a given session and invocation ID.
    """
    try:
        message_log = BedrockMessageLog(
            user_id=str(current_user.user_id),
            session_id=session_id,
            invocation_id=invocation_id,
            log_group_name=settings.LOG_GROUP_NAME,
            log_stream_name=settings.LOG_STREAM_NAME,
            feedback=BedrockMessageFeedbackType.LIKE,
        )
        bedrock_message_service.log_message(message_log=message_log, bedrock=bedrock, cloudwatch=cloudwatch)
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)


@copilot_router.post("/{session_id}/messages/{invocation_id}/dislike") # Create a new response
async def dislike_message(
    settings: SettingsDep,
    current_user: UserDep,
    bedrock: BedrockDep,
    cloudwatch: CloudwatchDep,
    session_id: str,
    invocation_id: str,
):
    """
    Dislike a message for a given session and invocation ID.
    """
    try:
        message_log = BedrockMessageLog(
            user_id=str(current_user.user_id),
            session_id=session_id,
            invocation_id=invocation_id,
            log_group_name=settings.LOG_GROUP_NAME,
            log_stream_name=settings.LOG_STREAM_NAME,
            feedback=BedrockMessageFeedbackType.LIKE,
        )
        bedrock_message_service.log_message(message_log=message_log, bedrock=bedrock, cloudwatch=cloudwatch)
    except HTTPException as e:
        raise HTTPException(status_code=e.code, detail=e.error)