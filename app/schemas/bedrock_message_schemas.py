from enum import StrEnum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, field_validator, validator


class BedrockMessageFeedbackType(StrEnum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"

class BedrockMessage(BaseModel):
    invocation_id: str = None
    query: str = None
    response_text: str = None
    citations: List[str] = []

class BedrockMessageCreate(BaseModel):
    agent_id: str = None
    agent_alias_id: str = None
    query: str
    memory_id: str = None
    session_id: str = None
    invocation_id: str = None
    session_state: Optional[Dict[str, Any]] = None
    
    @field_validator('memory_id')
    def ensure_memory_id_length(cls, v):
        if v is not None:
            return str(v).zfill(2)
        return v

class BedrockMessagesRead(BaseModel):
    session_id: str
    max_results: int

class BedrockMessageStore(BedrockMessage):
    session_id: str = None

class BedrockMessageLog(BaseModel):
    user_id: str = None
    session_id: str = None
    invocation_id: str = None
    log_group_name: str = None
    log_stream_name: str = None
    feedback: BedrockMessageFeedbackType = None

class BedrockQuery(BaseModel):
    query_text: str