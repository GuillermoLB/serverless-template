from pydantic import BaseModel, field_validator


class BedrockSession(BaseModel):
    session_id: str = None

class BedrockSessionSummarized(BedrockSession):
    session_id: str = None
    session_summary: str = None

class BedrockSessionCreate(BaseModel):
    encryption_key_arn: str = None

class BedrockSessionsRead(BedrockSession):
    session_id: str = None
    agent_id: str = None
    agent_alias_id: str = None
    max_items: int = None
    memory_id: str = None
    memory_type: str = None

    @field_validator('memory_id')
    def ensure_memory_id_length(cls, v):
        if v is not None:
            return str(v).zfill(2)
        return v

class BedrockSessionDelete(BedrockSession):
    pass