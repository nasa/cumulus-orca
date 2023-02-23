import boto3 
import json
import uuid
import time
import os
from botocore.client import Config
import logging


config = Config(read_timeout=600, retries={'total_max_attempts': 3})
client = boto3.client("lambda", config=config)

copy_to_archive_adapter_arn = os.environ["COPY_TO_ARCHIVE_ADAPTER_ARN"]
copy_to_archive_arn	= os.environ["COPY_TO_ARCHIVE_ARN"]
orca_recovery_bucket = os.environ["ORCA_RECOVERY_BUCKET"]

granule_id = uuid.uuid4().__str__()
provider_id = uuid.uuid4().__str__()
provider_name = uuid.uuid4().__str__()
createdAt_time = int((time.time() + 5) * 1000)
collection_shortname = uuid.uuid4().__str__()
collection_version = uuid.uuid4().__str__()
cumulus_bucket_name = "orca-sandbox-s3-provider"
execution_id = uuid.uuid4().__str__()
key_name = "PODAAC/SWOT/ancillary_data_input_forcing_ECCO_V4r4.tar.gz"

copy_to_archive_adapter_input_event = {
  "payload": {
    "granules": [
      {
        "granuleId": granule_id,
        "createdAt": createdAt_time,
        "files": [
          {
            "bucket": cumulus_bucket_name,
            "key": key_name
          }
        ]
      }
    ]
  },
  "cumulus_meta": {
    "execution_name": execution_id,

  },
  "task_config": {
    "providerId": provider_id,
    "executionId": execution_id,
    "collectionShortname": collection_shortname,
    "collectionVersion": collection_version,
    "defaultBucketOverride": orca_recovery_bucket
  }
}

response = client.invoke(
              FunctionName= copy_to_archive_adapter_arn,
              InvocationType="RequestResponse",  # Synchronous
              Payload=json.dumps(
                {
                  "input": copy_to_archive_adapter_input_event
                }
              )
            )