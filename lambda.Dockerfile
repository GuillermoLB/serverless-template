FROM public.ecr.aws/lambda/python:3.13

COPY app/ ./app/
COPY requirements.txt .

RUN python3.13 -m pip install -r requirements.txt -t .

# Set the correct handler (module.function)
CMD ["app.main.lambda_handler"]
