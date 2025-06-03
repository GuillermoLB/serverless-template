import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.schemas.bedrock_message_schemas import BedrockMessage, BedrockMessageCreate
from app.schemas.bedrock_response_schemas import BedrockResponse, BedrockResponseCreate


def extract_citations_from_attribution(attribution: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract citation information from attribution data.
    
    Args:
        attribution: Attribution data from a response chunk
        
    Returns:
        List of citation dictionaries
    """
    citations = []
    
    if 'citations' not in attribution:
        return citations
        
    for citation_data in attribution['citations']:
        if 'retrievedReferences' not in citation_data:
            continue
            
        for ref in citation_data['retrievedReferences']:
            citation = extract_source_from_reference(ref)
            if citation:
                citations.append(citation)
                
    return citations


def extract_source_from_reference(reference: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract source information from a reference.
    
    Args:
        reference: A single reference from retrieved references
        
    Returns:
        Dictionary with source information or None if no valid source
    """
    location = reference.get('location', {})
    location_type = location.get('type', 'Unknown')
    source = None
    
    # Extract the source URI based on location type
    if location_type == 'S3':
        source = location.get('s3Location', {}).get('uri')
    elif location_type == 'WEB':
        source = location.get('webLocation', {}).get('url')
    
    # Return source information if a valid source was found
    if source:
        return {
            'source': source,
            'location_type': location_type
        }
    
    return None

def process_agent_response(response: Dict[str, Any]) -> BedrockResponse:
    """
    Process the Bedrock agent response and extract the response text and citations.
    
    This function iterates through the event stream from the Bedrock agent response,
    accumulates the response text, and extracts citation sources as simple strings.
    
    Args:
        response: The raw response dictionary from the Bedrock agent
        
    Returns:
        ResponseRead: An object containing the agent's response text and a list of citation sources
    """
    
    # Initialize the response object
    agent_response = BedrockResponse(
        response_text="",
        citations=[]  # This will now be a list of strings
    )
    
    # Track unique sources to avoid duplicates
    unique_sources = set()
    
    try:
        # Get the event stream from the response
        event_stream = response.get('completion', response)
        
        # Process each event in the stream
        for event in event_stream:
            if 'chunk' not in event:
                continue
                
            chunk = event['chunk']
            
            # Process response text
            if 'bytes' in chunk:
                agent_response.response_text += chunk['bytes'].decode('utf-8')
            
            # Process citations
            if 'attribution' in chunk:
                # Extract citation information
                for citation_data in chunk.get('attribution', {}).get('citations', []):
                    for ref in citation_data.get('retrievedReferences', []):
                        # Extract source string based on location type
                        location = ref.get('location', {})
                        location_type = location.get('type', 'Unknown')
                        source = None
                        
                        if location_type == 'S3':
                            source = location.get('s3Location', {}).get('uri')
                        elif location_type == 'WEB':
                            source = location.get('webLocation', {}).get('url')
                        
                        # Add source to response if valid and unique
                        if source and source not in unique_sources:
                            unique_sources.add(source)
                            agent_response.citations.append(source)  # Now just adding the string
    
    except Exception as e:
        # Log the error but return a partial response if possible
        logging.error(f"Error processing agent response: {str(e)}")

    logger.info(f"Created response_text with length: {len(agent_response.response_text)}")
        
    return agent_response


def create_response(
    response_create: BedrockResponseCreate,
    bedrock: any,
) -> BedrockResponse:
    """
    Create a new message using the Bedrock agent.
    """
    logger.info(f"Creating response for the query: {response_create.query}")
    logger.info(f"Creating response for the user: {response_create.memory_id}")

    # Invoke the Bedrock agent
    invoke_agent_response = bedrock.invoke_agent(
        agentId=response_create.agent_id,
        agentAliasId=response_create.agent_alias_id,
        memoryId=response_create.memory_id,
        sessionId=response_create.session_id,
        inputText=response_create.query,
        sessionState=response_create.session_state,
        enableTrace=True
    )

    # TODO: try/except for invocation error
    processed_response = process_agent_response(invoke_agent_response)


    return processed_response
