import logging
import logging.config  # <-- Add this line
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from mangum import Mangum

from app.core.log_config import LogConfig
from app.dependencies import get_settings
from app.routers.token_router import tokens_router
from app.routers.user_router import users_router
from app.routers.copilot_router import copilot_router


logging.config.dictConfig(LogConfig().model_dump())

logger = logging.getLogger(__name__)

settings = get_settings()


app = FastAPI(
    title="Authentication API",
    description="""
""",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Users",
            "description": "User management and authentication",
        },
    ]
)


# Include API routes
app.include_router(users_router)
app.include_router(tokens_router)
app.include_router(copilot_router)


# Middleware to log requests and responses
@app.middleware("http")
async def log_request_response(request: Request, call_next):
    request_id = str(uuid4())
    start_time = time.time()

    # Log request metadata
    path = request.url.path + \
        ("?" + request.url.query if request.url.query else "")
    logger.info(f"Request {request_id}: {request.method} {path}")

    # Process request
    response = await call_next(request)

    # Log response metadata
    process_time = round((time.time() - start_time) * 1000)
    logger.info(
        f"Response {request_id}: Status={response.status_code} Duration={process_time}ms "
        f"Method={request.method} Path={path}"
    )

    return response


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # Use the logger you've defined
    logger.debug(f"API Event: {event}")

    # Rest of your handler code...
    handler = Mangum(app, api_gateway_base_path=settings.API_GATEWAY_BASE_PATH)
    response = handler(event, context)
    return response


@app.get("/")
def health_check():
    return {"status": "OK"}
