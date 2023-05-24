import os
import unittest
import uuid
from dataclasses import dataclass
from unittest import mock

# noinspection PyPackageRequirements
import pytest

import orca_recovery_adapter


class TestOrcaRecoveryAdapter(unittest.TestCase):

    def test_orca_recovery_adapter_happy_path(
        self,
    ):
        """
        Runs against AWS to request recovery of a file.
        """
        def lambda_context():
            """
            Sets up an object with the information required for inject_lambda_context.
            """
            @dataclass
            class LambdaContext:
                function_name: str = "test"
                memory_limit_in_mb: int = 128
                invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
                aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

            return LambdaContext()

        # PREFIX-orca-primary
        orca_recovery_bucket = os.environ["ORCA_RECOVERY_BUCKET"]
        # PREFIX-public
        cumulus_bucket_name = os.environ["CUMULUS_BUCKET_NAME"]
        # PREFIX-internal
        system_bucket_name = os.environ["CUMULUS_SYSTEM_BUCKET_NAME"]
        # MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf
        key_name = os.environ["OBJECT_KEY_NAME"]
        file_name = os.path.basename(key_name)
        _, file_extension = os.path.splitext(file_name)
        collection_id = uuid.uuid4().__str__()
        granule_id = os.environ["GRANULE_ID"]

        orca_recovery_adapter_input_event = {
            "payload": {
                "granules": [
                    {
                        "collectionId": collection_id,
                        "granuleId": granule_id,
                        "files": [
                            {
                                "fileName": file_name,
                                "key": key_name,
                                "bucket": orca_recovery_bucket
                            }
                        ]
                    }
                ]
            },
            "task_config": {
                "buckets": "{$.meta.buckets}",
                "fileBucketMaps": "{$.meta.collection.files}",
                "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
                "asyncOperationId": "{$.cumulus_meta.asyncOperationId}",
                "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
                "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}",
                "defaultRecoveryTypeOverride":
                    "{$.meta.collection.meta.orca.defaultRecoveryTypeOverride}"
            },
            "meta": {
                "buckets": {
                    "public": {"name": cumulus_bucket_name, "type": "public"},
                    "orca_default": {"name": orca_recovery_bucket, "type": "orca"}
                },
                "collection": {
                    "meta": {
                        "orca": {
                            "excludedFileExtensions": [".blah"]
                        }
                    },
                    "files": [
                        {
                            "regex": ".*" + file_extension,
                            "sampleFileName": "blah" + file_extension,
                            "bucket": "public"
                        }
                    ]
                }
            },
            "cumulus_meta": {
                "system_bucket": system_bucket_name
            }
        }

        expected_output = {
            'payload': {
                'granules': [{
                    'collectionId': collection_id,
                    'granuleId': granule_id,
                    'keys': [{
                        'key': key_name, 'destBucket': cumulus_bucket_name
                    }],
                    'recoverFiles': [{
                        'success': True,
                        'filename': file_name,
                        'keyPath': key_name,
                        'restoreDestination': cumulus_bucket_name,
                        's3MultipartChunksizeMb': None,
                        'statusId': 1,
                        'requestTime': mock.ANY,
                        'lastUpdate': mock.ANY
                    }]
                }],
                'asyncOperationId': mock.ANY
            },
            'task_config': orca_recovery_adapter_input_event["task_config"],
            'meta': orca_recovery_adapter_input_event["meta"],
            'cumulus_meta': orca_recovery_adapter_input_event["cumulus_meta"],
            'exception': 'None'}

        # noinspection PyTypeChecker
        result = orca_recovery_adapter.handler(
            orca_recovery_adapter_input_event,
            lambda_context(),
        )
        self.assertEqual(expected_output, result)


if __name__ == '__main__':
    unittest.main()
