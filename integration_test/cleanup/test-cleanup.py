import boto3
import os
from orca_shared.database import shared_db
from sqlalchemy import text
from sqlalchemy.future import Engine
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError


LOGGER = Logger()

# os.env keys
recovery_bucket_name = os.environ["orca_RECOVERY_BUCKET_NAME"]
source_bucket_name = os.environ["SOURCE_BUCKET_NAME"]

# grab the objects to be deleted
s3 = boto3.client('s3')
result = s3.list_objects_v2(
    Bucket=source_bucket_name,
    Prefix='test'
)
filenames = []
for item in result['Contents']:
    files = item['Key']
    filenames.append(files)
LOGGER.info(filenames)

# Delete objects from source and recovery buckets
for object in filenames:
    response_source = s3.delete_object(
        Bucket=source_bucket_name,
        Key=object,
    )
    response_destination = s3.delete_object(
        Bucket=recovery_bucket_name,
        Key=object,
    )

# verify objects are deleted from buckets
for object in filenames:
    try:
        head_object_output = s3.head_object(
        Bucket=source_bucket_name,Key=object
        )
    except ClientError as error:
        if error.response['Error']['Code'] == '404':
            LOGGER.info(f"{object} not found in {source_bucket_name}. Test passed")
for object in filenames:
    try:
        head_object_output = s3.head_object(
        Bucket=recovery_bucket_name,Key=object
        )
    except ClientError as error:
        if error.response['Error']['Code'] == '404':
            LOGGER.info(f"{object} not found in {recovery_bucket_name}. Test passed")

#delete from catalog
try:
    db_connect_info_secret_arn = os.environ["DB_CONNECT_INFO_SECRET_ARN"]
except KeyError:
    LOGGER.error("DB_CONNECT_INFO_SECRET_ARN environment value not found.")
    raise
db_connect_info = shared_db.get_configuration(db_connect_info_secret_arn)
engine = shared_db.get_user_connection(db_connect_info)
print(engine)

# def delete_sql() -> text:  # pragma: no cover
#     return text(
#         """
#         select * from orca.recovery_status"""
#     )

# with engine.begin() as connection:
#     connection.execute(
#         delete_sql()
#     )


    
# try:
#     with engine.begin() as connection:
#         connection.execute(
#             create_job_sql(),
#             [
#                 {
#                     "job_id": job_id,
#                     "granule_id": granule_id,
#                     "status_id": job_status.value,
#                     "request_time": request_time,
#                     "completion_time": job_completion_time,
#                     "archive_destination": archive_destination,
#                 }
#             ],
#         )
#         if len(file_parameters) > 0:
#             connection.execute(create_file_sql(), file_parameters)
# except Exception as sql_ex:
#     # Can't use f"" because of '{}' bug in CumulusLogger.
#     LOGGER.error(
#         "Error while creating statuses for job '{job_id}': {sql_ex}",
#         job_id=job_id,
#         sql_ex=sql_ex,
#     )
#     raise

