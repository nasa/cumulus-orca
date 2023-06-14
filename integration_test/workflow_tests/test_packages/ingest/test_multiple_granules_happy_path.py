import json
import time
import uuid
from typing import Dict, List
from unittest import TestCase, mock

import boto3

import helpers
from custom_logger import CustomLoggerAdapter

# Set the logger
logger = CustomLoggerAdapter.set_logger(__name__)

recovery_request_record_happy_path_filename = "RecoveryHappyPath"


class TestMultipleGranulesHappyPath(TestCase):

    def test_multiple_granules_happy_path(self):
        self.maxDiff = None
        use_large_file = True  # This should not be checked in with any value other than `True`
        """
        - If multiple granules are provided, should store them in DB as well as in recovery bucket.
        - Files stored in GLACIER are also ingest-able.
        - Large files should not cause timeout.
        """
        try:
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()
            granule_id_1 = uuid.uuid4().__str__()
            granule_id_2 = uuid.uuid4().__str__()
            provider_id = uuid.uuid4().__str__()
            provider_name = uuid.uuid4().__str__()
            # noinspection PyPep8Naming
            createdAt_time = int((time.time() + 5) * 1000)
            collection_name = uuid.uuid4().__str__()
            collection_version = uuid.uuid4().__str__()
            collection_id = collection_name + "___" + collection_version
            # standard bucket where test files will be copied
            cumulus_bucket_name = "orca-sandbox-s3-provider"
            recovery_bucket_name = helpers.recovery_bucket_name
            excluded_filetype = []
            name_1 = uuid.uuid4().__str__() + ".hdf"  # refers to file1.hdf
            key_name_1 = "test/" + uuid.uuid4().__str__() + "/" + name_1
            file_1_hash = uuid.uuid4().__str__()
            file_1_hash_type = uuid.uuid4().__str__()
            # Upload the randomized file to source bucket
            boto3.client('s3').upload_file(
                "file1.hdf", cumulus_bucket_name, key_name_1
            )
            execution_id = uuid.uuid4().__str__()

            if use_large_file:
                # file for large file test
                # Since this file is 191GB, it should already exist in the source bucket.
                name_2 = "ancillary_data_input_forcing_ECCO_V4r4.tar.gz"
                key_name_2 = "PODAAC/SWOT/" + name_2
            else:
                name_2 = uuid.uuid4().__str__() + ".hdf"  # refers to file1.hdf
                key_name_2 = "test/" + uuid.uuid4().__str__() + "/" + name_2
                # Upload the randomized file to source bucket
                boto3.client('s3').upload_file(
                    "file1.hdf", cumulus_bucket_name, key_name_2
                )
            copy_to_archive_input = {
                "payload": {
                    "granules": [
                        {
                            "granuleId": granule_id_1,
                            "createdAt": createdAt_time,
                            "files": [
                                {
                                    "bucket": cumulus_bucket_name,
                                    "key": key_name_1,
                                    "checksum": file_1_hash,
                                    "checksumType": file_1_hash_type,
                                }
                            ]
                        },
                        {
                            "granuleId": granule_id_2,
                            "createdAt": createdAt_time,
                            "files": [
                                {
                                    "bucket": cumulus_bucket_name,
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
                                "excludedFileExtensions": excluded_filetype
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
                        "granuleId": granule_id_1,
                        "createdAt": createdAt_time,
                        "files": [
                            {
                                "bucket": cumulus_bucket_name,
                                "key": key_name_1,
                                "checksum": file_1_hash,
                                "checksumType": file_1_hash_type
                            }
                        ]
                    },
                    {
                        "granuleId": granule_id_2,
                        "createdAt": createdAt_time,
                        "files": [
                            {
                                "bucket": cumulus_bucket_name,
                                "key": key_name_2,
                            }
                        ]
                    }
                ],
                "copied_to_orca": [
                    "s3://" + cumulus_bucket_name + "/" + key_name_1,
                    "s3://" + cumulus_bucket_name + "/" + key_name_2
                ]
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
                "Expected ingest step function output not returned.",
            )
            s3_versions = []
            # verify that the objects exist in recovery bucket
            try:
                for key in [
                    key_name_1,
                    key_name_2,
                ]:
                    # If ORCA ever migrates its functionality to DR,
                    # and cross-account access is no longer granted,
                    # use boto3.Session(profile_name="yourAWSConfigureProfileName").client(...
                    # to use a differently configured aws access key
                    head_object_output = boto3.client("s3").head_object(
                        Bucket=recovery_bucket_name, Key=key)
                    self.assertEqual(
                        200,
                        head_object_output["ResponseMetadata"]["HTTPStatusCode"],
                        f"Error searching for object {key} in the {recovery_bucket_name}",
                    )
                    self.assertEqual(
                        "GLACIER",
                        head_object_output["StorageClass"]
                    )
                    s3_versions.append(head_object_output["VersionId"])
            except Exception as ex:
                logger.error(ex)
                raise

            # Let the catalog update
            time.sleep(10)
            # noinspection PyArgumentList
            catalog_output = helpers.post_to_api(
                my_session,
                helpers.api_url + "/catalog/reconcile/",
                data=json.dumps(
                    {
                        "pageIndex": 0,
                        "collectionId": [collection_id],
                        "granuleId": [
                            granule_id_1,
                            granule_id_2,
                        ],
                        "endTimestamp": int((time.time() + 5) * 1000),
                    }
                ),
                headers={"Host": helpers.aws_api_name},
            )
            self.assertEqual(
                200, catalog_output.status_code, f"Error occurred while contacting API: "
                                                 f"{catalog_output.content}"
            )
            expected_catalog_output_granules = [{
                "providerId": provider_id,
                "collectionId": collection_id,
                "id": granule_id_1,
                "createdAt": createdAt_time,
                "executionId": execution_id,
                "files": [
                    {
                        "name": name_1,
                        "cumulusArchiveLocation": cumulus_bucket_name,
                        "orcaArchiveLocation": recovery_bucket_name,
                        "keyPath": key_name_1,
                        "sizeBytes": 205640819682 if use_large_file else 6,
                        "hash": file_1_hash, "hashType": file_1_hash_type,
                        "storageClass": "GLACIER",
                        "version": s3_versions[0],
                    }
                ],
                "ingestDate": mock.ANY,
                "lastUpdate": mock.ANY
            },
                {
                    "providerId": provider_id,
                    "collectionId": collection_id,
                    "id": granule_id_2,
                    "createdAt": createdAt_time,
                    "executionId": execution_id,
                    "files": [
                        {
                            "name": name_2,
                            "cumulusArchiveLocation": cumulus_bucket_name,
                            "orcaArchiveLocation": recovery_bucket_name,
                            "keyPath": key_name_2,
                            "sizeBytes": 6,
                            "hash": None, "hashType": None,
                            "storageClass": "GLACIER",
                            "version": s3_versions[1],
                        }
                    ],
                    "ingestDate": mock.ANY,
                    "lastUpdate": mock.ANY
                }]
            expected_catalog_output = {
                "anotherPage": False,
                "granules": mock.ANY
            }
            catalog_output_json = catalog_output.json()
            self.assertEqual(
                expected_catalog_output,
                catalog_output_json,
                "Expected API output not returned.",
            )
            # Make sure all given granules are present without checking order.
            self.assertCountEqual(
                expected_catalog_output_granules,
                catalog_output_json["granules"],
                "Expected API output granules not returned."
            )

            # recovery check
            self.partial_test_recovery_happy_path(
                collection_id, granule_id_1, name_1, key_name_1, recovery_bucket_name)
        except Exception as ex:
            logger.error(ex)
            raise

    def partial_test_recovery_happy_path(
        self, collection_id: str, granule_id: str, file_name: str,
        file_key: str, orca_bucket_name: str
    ):
        target_bucket = helpers.buckets["private"]["name"]
        # noinspection PyTypeChecker
        recovery_request_record = helpers.RecoveryRequestRecord([
            helpers.RecoveryRequestGranule(collection_id, granule_id, [
                helpers.RecoveryRequestFile(file_name, file_key, orca_bucket_name, target_bucket)
            ])
        ], None)
        step_function_results = self.initiate_recovery(
            recovery_request_record=recovery_request_record,
            file_bucket_maps=[
                {
                    "regex": ".*",
                    "bucket": "private"
                }]
        )
        self.assertEqual(
            "SUCCEEDED",
            step_function_results["status"],
            "Error occurred while starting step function.",
        )
        expected_output = {
            "granules": [
                {
                    "collectionId": collection_id,
                    "granuleId": granule_id,
                    "keys": [
                        {
                            "key": file_key,
                            "destBucket": target_bucket
                        }
                    ],
                    "recoverFiles": [
                        {
                            "success": True,
                            "filename": file_name,
                            "keyPath": file_key,
                            "restoreDestination": target_bucket,
                            "s3MultipartChunksizeMb": None,
                            "statusId": 1,
                            "requestTime": mock.ANY,
                            "lastUpdate": mock.ANY
                        }
                    ]
                }
            ],
            "asyncOperationId": mock.ANY
        }
        actual_output = json.loads(step_function_results["output"])
        self.assertEqual(
            expected_output,
            actual_output,
            "Expected recovery step function output not returned.",
        )

        recovery_request_record.async_operation_id = actual_output["asyncOperationId"]

        helpers.create_recovery_request_record(recovery_request_record_happy_path_filename,
                                               recovery_request_record)

    @staticmethod
    def initiate_recovery(
        recovery_request_record: helpers.RecoveryRequestRecord, file_bucket_maps: List[Dict],
    ):
        recovery_step_function_input = {
            "payload": {
                "granules": [{
                    "collectionId": granule.collection_id,
                    "granuleId": granule.granule_id,
                    "files": [{
                        "fileName": file.file_name,
                        "key": file.file_key,
                        "bucket": file.orca_bucket_name
                    } for file in granule.files],
                } for granule in recovery_request_record.granules],
            },
            "config": {
                "buckets": helpers.buckets,
                "fileBucketMaps": file_bucket_maps,
                "excludedFileExtensions": [],
                "asyncOperationId": None,
                "s3MultipartChunksizeMb": None,
                "defaultBucketOverride": None,
                "defaultRecoveryTypeOverride": None
            }
        }

        logger.info("Sending event to recovery step function.")
        logger.info(recovery_step_function_input)

        execution_info = boto3.client("stepfunctions").start_execution(
            stateMachineArn=helpers.orca_recovery_step_function_arn,
            input=json.dumps(recovery_step_function_input, indent=4),
        )

        step_function_results = helpers.get_state_machine_execution_results(
            execution_info["executionArn"]
        )

        return step_function_results
