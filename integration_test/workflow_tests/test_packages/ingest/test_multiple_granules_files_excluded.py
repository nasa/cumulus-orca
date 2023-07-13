import json
import time
import uuid
from unittest import TestCase, mock

import boto3

# noinspection PyPackageRequirements
from botocore.exceptions import ClientError

import helpers
from custom_logger import CustomLoggerAdapter

# Set the logger
logger = CustomLoggerAdapter.set_logger(__name__)


class TestMultipleGranules(TestCase):
    def test_multiple_granules_files_excluded_passes(self):
        self.maxDiff = None
        """
        Files are excluded from recovery due to excluded_filetype being set.
        """
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()
            granule_id = uuid.uuid4().__str__()
            provider_id = uuid.uuid4().__str__()
            provider_name = uuid.uuid4().__str__()
            # noinspection PyPep8Naming
            createdAt_time = int((time.time() + 5) * 1000)
            collection_name = uuid.uuid4().__str__()
            collection_version = uuid.uuid4().__str__()
            recovery_bucket_name = helpers.recovery_bucket_name
            # standard bucket where test file will be copied
            bucket_name = "orca-sandbox-s3-provider"
            excluded_filetype = [".hdf"]
            file_name = uuid.uuid4().__str__() + ".hdf"  # refers to file1.hdf
            key_name = "test/" + uuid.uuid4().__str__() + "/" + file_name
            execution_id = uuid.uuid4().__str__()

            # Upload the randomized file to source bucket
            boto3.client('s3').upload_file("file1.hdf",
                                           bucket_name, key_name)
            copy_to_archive_input = {
                "payload": {
                    "granules": [
                        {
                            "granuleId": granule_id,
                            "createdAt": createdAt_time,
                            "files": [
                                {
                                    "bucket": bucket_name,
                                    "key": key_name
                                }
                            ]
                        }
                    ]
                },
                "meta": {
                    "provider": {
                        "id": provider_id,
                        "name": provider_name
                    },
                    "collection": {
                        "meta": {
                            "orca": {
                                "excludedFileExtensions":
                                    excluded_filetype
                            }
                        },
                        "name": collection_name,
                        "version": collection_version
                    }
                },
                "cumulus_meta": {
                    "execution_name": execution_id
                }
            }

            expected_output = {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "createdAt": createdAt_time,
                        "files": [
                            {
                                "bucket": bucket_name,
                                "key": key_name
                            }
                        ]
                    }
                ],
                "copied_to_orca": []
            }

            execution_info = boto3.client("stepfunctions").start_execution(
                stateMachineArn=helpers.orca_copy_to_archive_step_function_arn,
                input=json.dumps(copy_to_archive_input, indent=4),
            )

            step_function_results = helpers.get_state_machine_execution_results(
                execution_info["executionArn"],
                maximum_duration_seconds=30,
            )

            self.assertEqual(
                "SUCCEEDED",
                step_function_results["status"],
                "Error occurred while starting step function.",
            )
            actual_output = json.loads(step_function_results["output"])
            self.assertEqual(
                expected_output,
                actual_output,
                "Expected step function output not returned.",
            )

            # verify that the object does NOT exist in recovery bucket
            try:
                head_object_output = boto3.client("s3").head_object(
                    Bucket=recovery_bucket_name, Key=key_name)
                if head_object_output["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    raise Exception(f"{key_name} already exists"
                                    f" or was incorrectly ingested to {recovery_bucket_name}")
            except ClientError as err:
                self.assertEqual(
                    "404",
                    err.response["Error"]["Code"]
                )

            # Let the catalog update
            time.sleep(10)
            # noinspection PyArgumentList
            catalog_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/catalog/reconcile/",
                data=json.dumps(
                    {
                        "pageIndex": 0,
                        "collectionId": [collection_name + "___" + collection_version],
                        "granuleId": [granule_id],
                        "endTimestamp": int((time.time() + 5) * 1000),
                    }
                ),
                headers={"Host": helpers.aws_api_name},
            )
            self.assertEqual(
                200, catalog_output.status_code, f"Error occurred while contacting API: "
                                                 f"{catalog_output.content}"
            )
            self.assertEqual(
                {
                    "anotherPage": False,
                    "granules": [
                        {
                            "id": granule_id,
                            "collectionId": collection_name + "___" + collection_version,
                            "createdAt": createdAt_time,
                            "executionId": execution_id,
                            "providerId": provider_id,
                            "files": [],
                            "ingestDate": mock.ANY,
                            "lastUpdate": mock.ANY
                        }
                    ]
                },
                catalog_output.json(),
                "Expected API output not returned.",
            )
        except Exception as ex:
            logger.error(ex)
            raise
