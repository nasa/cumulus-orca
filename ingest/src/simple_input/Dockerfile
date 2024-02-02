# lambda base image for Docker from AWS
FROM --platform=linux/arm64 public.ecr.aws/lambda/python:3.11

COPY dist/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt \
    && rm ${LAMBDA_TASK_ROOT}/requirements.txt 

COPY src/ ${LAMBDA_TASK_ROOT}
CMD ["simple_input.adapter.lambda_handler"]