import json
import logging
import time
import uuid
from unittest import TestCase

import boto3

import helpers


class TestMultipleGranulesHappyPath(TestCase):
    def test_multiple_granules_happy_path(self):
        """
        If multiple granules are provided, should store them in DB as well as in recovery bucket.
        """
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()
            granule_id_1 = uuid.uuid4().__str__()
            granule_id_2 = uuid.uuid4().__str__()
            provider_id = uuid.uuid4().__str__()
            provider_name = uuid.uuid4().__str__()

            collection_name = uuid.uuid4().__str__()
            collection_version = uuid.uuid4().__str__()
            bucket_name = "orca-sandbox-s3-provider"  # standard bucket where initial file exists
            recovery_bucket_name = "rhrh-orca-primary"
            excluded_filetype = []
            key_name_1 = "PODAAC/SWOT/ancillary_data_input_forcing_ECCO_V4r4.tar.gz"
            key_name_2 = "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf"
            execution_id = uuid.uuid4().__str__()

            copy_to_archive_input = {
                "payload": {
                    "granules": [
                    {
                        "granuleId": granule_id_1,
                        "createdAt": 628021800000,
                        "files": [
                        {
                            "bucket": bucket_name,
                            "key": key_name_1
                        }
                        ]
                    },
                    {
                        "granuleId": granule_id_2,
                        "createdAt": 628021800001,
                        "files": [
                        {
                            "bucket": bucket_name,
                            "key": key_name_2
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
                "payload": {
                    "granules": [
                    {
                        "granuleId": granule_id_1,
                        "createdAt": 628021800000,
                        "files": [
                        {
                            "bucket": bucket_name,
                            "key": key_name_1,
                        }
                        ]
                    },
                    {
                        "granuleId": granule_id_2,
                        "createdAt": 628021800001,
                        "files": [
                        {
                            "bucket": bucket_name,
                            "key": key_name_2,
                        }
                        ]
                    }
                    ],
                    "copied_to_orca": [
                    "s3://" + bucket_name + "/" + key_name_1,
                    "s3://" + bucket_name + "/" + key_name_2
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
                },
                "task_config": {
                    "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
                    "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
                    "providerId": "{$.meta.provider.id}",
                    "providerName": "{$.meta.provider.name}",
                    "executionId": "{$.cumulus_meta.execution_name}",
                    "collectionShortname": "{$.meta.collection.name}",
                    "collectionVersion": "{$.meta.collection.version}",
                    "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}",
                    "defaultStorageClassOverride": "{$.meta.collection.meta.orca.defaultStorageClassOverride}"
                },
                "exception": "None"
                }

            execution_info = boto3.client("stepfunctions").start_execution(
                stateMachineArn=helpers.orca_copy_to_archive_step_function_arn,
                input=json.dumps(copy_to_archive_input, indent=4),
            )

            step_function_results = helpers.get_state_machine_execution_results(
                execution_info["executionArn"]
            )

            self.assertEqual(
                "SUCCEEDED",
                step_function_results["status"],
                "Error occurred while starting step function.",
            )
            self.assertEqual(
                expected_output,
                json.loads(step_function_results["output"]),
                "Expected step function output not returned.",
            )
            # verify that the objects exist in recovery bucket
            try:
                for keys in [key_name_1, key_name_2]:
                    output = boto3.client("s3").head_object(Bucket=recovery_bucket_name, Key=keys)
                    self.assertEqual(
                        200,
                        output["ResponseMetadata"]["HTTPStatusCode"],
                        f"object {keys} does not exist in the {recovery_bucket_name}",
                    )            
            except Exception as ex:
                return  ex

            catalog_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/catalog/reconcile/",
                data=json.dumps(
                    {
                        "pageIndex": 0,
                        "providerId": [provider_id],
                        "granuleId": [granule_id_1, granule_id_2],
                        "endTimestamp": int((time.time() + 5) * 1000),
                    }
                ),
                headers={"Host": helpers.aws_api_name},
            )
            self.assertEqual(
                200, catalog_output.status_code, "Error occurred while contacting API."
            )
            self.assertEqual(
                {"granules": [granule_id_1, granule_id_2], "anotherPage": False},
                catalog_output.json(),
                "Expected empty granule list not returned.",
            )
        except Exception as ex:
            logging.error(ex)
            raise