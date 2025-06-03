import io
import json
import pytest
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import botocore
from botocore.response import StreamingBody

# Original botocore _make_api_call function
orig = botocore.client.BaseClient._make_api_call


# Mocked botocore _make_api_call function
def mock_bedrock_make_api_call(self, operation_name, kwarg):
    if operation_name == "CreateSession":
        response = {
            "sessionId": str(uuid.uuid4()),
            "sessionArn": f"arn:aws:bedrock:us-east-1:123456789012:session/{str(uuid.uuid4())}"
        }
        return response
    
    if operation_name == "GetAgentMemory":
        response = {
            "memoryContents": [
                {
                    "sessionSummary": {
                        "sessionId": str(uuid.uuid4()),
                        "summaryText": "Test conversation about Python"
                    }
                }
            ]
        }
        return response
    # If we don't want to patch the API call
    return orig(self, operation_name, kwarg)


# @pytest.fixture
# def mock_bedrock_client(mocker):
#     """Create a comprehensive mock for Bedrock client"""
#     mock_client = MagicMock()
    
#     # Mock create_session
#     mock_client.create_session.return_value = {
#         "sessionId": str(uuid.uuid4()),
#         "sessionArn": f"arn:aws:bedrock:us-east-1:123456789012:session/{str(uuid.uuid4())}"
#     }
    
#     # Mock invoke_agent with a proper response structure
#     mock_client.invoke_agent.return_value = {
#         "completion": [
#             {
#                 "chunk": {
#                     "bytes": "This is a mock response from Bedrock".encode("utf-8")
#                 }
#             },
#             {
#                 "chunk": {
#                     "attribution": {
#                         "citations": [
#                             {
#                                 "retrievedReferences": [
#                                     {
#                                         "location": {
#                                             "type": "WEB",
#                                             "webLocation": {
#                                                 "url": "https://example.com/doc1"
#                                             }
#                                         }
#                                     }
#                                 ]
#                             }
#                         ]
#                     }
#                 }
#             }
#         ]
#     }
    
#     # Mock get_agent_memory
#     mock_client.get_agent_memory.return_value = {
#         "memoryContents": [
#             {
#                 "sessionSummary": {
#                     "sessionId": "test-session-1",
#                     "summaryText": "Test conversation about Python"
#                 }
#             }
#         ]
#     }
    
#     # Other Bedrock methods
#     mock_client.create_invocation.return_value = {"invocationId": str(uuid.uuid4())}
#     mock_client.put_invocation_step.return_value = {}
#     mock_client.end_session.return_value = {}
#     mock_client.delete_session.return_value = {}
#     mock_client.list_invocations.return_value = {
#         "invocationSummaries": [
#             {"invocationId": "test-invocation-1", "startTime": datetime.now()}
#         ]
#     }
#     mock_client.list_invocation_steps.return_value = {
#         "invocationStepSummaries": [
#             {"invocationStepId": "step-1", "invocationStepTime": datetime.now()}
#         ]
#     }
#     mock_client.get_invocation_step.return_value = {
#         "invocationStep": {
#             "invocationStepId": "step-1",
#             "payload": {
#                 "contentBlocks": [
#                     {"text": "Test message content"}
#                 ]
#             }
#         }
#     }
    
#     return mock_client

# @pytest.fixture
# def mock_cloudwatch_client(mocker):
#     """Create a mock for CloudWatch Logs client"""
#     mock_client = MagicMock()
#     mock_client.describe_log_streams.return_value = {
#         "logStreams": [{"uploadSequenceToken": "token123"}]
#     }
#     mock_client.put_log_events.return_value = {}
#     return mock_client



