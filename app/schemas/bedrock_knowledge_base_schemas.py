from enum import StrEnum
from pydantic import BaseModel


class BedrockDataSourceType(StrEnum):
    WEB = "WEB"
    S3 = "S3"


class BedrockKnowledgeBaseModel(BaseModel):
    knowledge_base_id: str
    data_sources: dict[BedrockDataSourceType, str]
