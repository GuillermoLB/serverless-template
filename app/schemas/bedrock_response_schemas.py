from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BedrockResponse(BaseModel):
    response_text: str = None
    citations: List[str] = []

class BedrockResponseCreate(BaseModel):
    agent_id: str = None
    agent_alias_id: str = None
    query: str
    memory_id: str = None
    session_id: str = None
    invocation_id: str = None
    session_state: Optional[Dict[str, Any]] = None
    
class BedrockResponsesRead(BaseModel):
    agent_alias_id: str = None
    session_id: str = None
    invocation_id: str = None