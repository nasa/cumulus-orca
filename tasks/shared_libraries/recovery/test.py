
import os, boto3
from cumulus_logger import CumulusLogger

# instantiate CumulusLogger
logger = CumulusLogger()

AWS_REGION = 'us-west-2'

def get_aws_region():
    # Get the AWS_REGION defined runtime environment reserved variable
    logger.debug("Getting environment variable AWS_REGION value.")
    aws_region = os.getenv(AWS_REGION, None)
    print(aws_region)
    if aws_region is None or len(aws_region) == 0:
        message = "Runtime environment variable AWS_REGION is not set."
        logger.critical(message)
        raise Exception(message)
    return aws_region

mysqs_resource = boto3.resource("sqs", region_name= get_aws_region())
print(mysqs_resource)