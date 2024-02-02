from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from .schema import Input, Output
from .use_cases import get_settings

metrics = Metrics()
tracer = Tracer()
logger = Logger()
app = APIGatewayRestResolver(enable_validation=True)
app.enable_swagger()


@app.post("/ingest")
@tracer.capture_method
def ingest_granule(input: Input) -> Output:
    settings = get_settings(logger, input.configuration_overrides)
    return Output(message=f"{input.data} with a config of {settings.model_dump()}", errorCode=None)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.LAMBDA_FUNCTION_URL)
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info("Log additional key", extra={"user_id": "1", "e": event})
    return app.resolve(event, context)


if __name__ == "__main__":
    print(app.get_openapi_json_schema())
