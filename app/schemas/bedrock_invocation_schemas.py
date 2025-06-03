from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class BedrockInvocation(BaseModel):
    invocation_id: str = None

class BedrockInvocationCreate(BaseModel):
    invocation_id: str = None
    description: str = None

class BedrockInvocationRead(BedrockInvocation):
    pass