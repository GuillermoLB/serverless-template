from src.Model.copilot.bedrock_knowledge_base_schemas import BedrockDataSourceType, BedrockKnowledgeBaseModel


def ingest_data_source(bedrock: any, knowledge_base: BedrockKnowledgeBaseModel, source: BedrockDataSourceType) -> None:
    start_job_response = bedrock.start_ingestion_job(
        knowledgeBaseId= knowledge_base.knowledge_base_id,
        dataSourceId= knowledge_base.data_sources[source]
    )