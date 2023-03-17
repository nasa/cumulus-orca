import os
import time
import unittest
import uuid
from unittest.mock import Mock

import boto3

import copy_to_archive_adapter


class TestCopyToArchiveAdapter(unittest.TestCase):
    def test_copy_to_archive_adapter_happy_path(self):

        orca_recovery_bucket = os.environ["ORCA_RECOVERY_BUCKET"]
        cumulus_bucket_name = os.environ["CUMULUS_BUCKET_NAME"]
        key_name = os.environ["OBJECT_KEY_NAME"]
        granule_id = uuid.uuid4().__str__()
        provider_id = uuid.uuid4().__str__()
        createdAt_time = int((time.time() + 5) * 1000)
        collection_shortname = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        execution_id = uuid.uuid4().__str__()

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
          "task_config": {
            "providerId": provider_id,
            "executionId": execution_id,
            "collectionShortname": collection_shortname,
            "collectionVersion": collection_version,
            "defaultBucketOverride": orca_recovery_bucket
          }
        }

        expected_output = {
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
            ],
            "copied_to_orca": [
              "s3://" + cumulus_bucket_name + "/" + key_name,
            ]
          },
          "task_config": {
            "providerId": provider_id,
            "executionId": execution_id,
            "collectionShortname": collection_shortname,
            "collectionVersion": collection_version,
            "defaultBucketOverride": orca_recovery_bucket
          },
          "exception": "None"
        }
        context = Mock()
        result = copy_to_archive_adapter.handler(copy_to_archive_adapter_input_event, context)
        self.assertEqual(result, expected_output)
        # verify that the object exists in recovery bucket
        try:
            head_object_output = boto3.client("s3").head_object(
                Bucket=orca_recovery_bucket, Key=key_name)
            self.assertEqual(
                200,
                head_object_output["ResponseMetadata"]["HTTPStatusCode"],
                f"Error searching for object {key_name} in the {orca_recovery_bucket}",
            )
        except Exception as ex:
            raise ex


if __name__ == '__main__':
    unittest.main()
