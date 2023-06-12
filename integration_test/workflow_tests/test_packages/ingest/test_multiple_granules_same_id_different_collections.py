import json
import time
import uuid
from unittest import TestCase, mock

import boto3

import helpers
from custom_logger import CustomLoggerAdapter

# Set the logger
logging = CustomLoggerAdapter.set_logger(__name__)


class TestMultipleGranulesSameIdDifferentCollections(TestCase):

    def test_multiple_granules_same_id_different_collections(self):
        self.maxDiff = None
        """
        - The same granule id should be allowed in multiple collections.
        """
        try:
            self.assertCountEqual([], [], "Didn't match")
            # Set up Orca API resources
            # ---
            my_session = helpers.create_session()
            granule_id = uuid.uuid4().__str__()
            provider_id = uuid.uuid4().__str__()
            provider_name = uuid.uuid4().__str__()
            # noinspection PyPep8Naming
            createdAt_time = int((time.time() + 5) * 1000)
            collection_name_1 = uuid.uuid4().__str__()
            collection_version_1 = uuid.uuid4().__str__()
            collection_name_2 = uuid.uuid4().__str__()
            collection_version_2 = uuid.uuid4().__str__()
            # standard bucket where test files will be copied
            cumulus_bucket_name = "orca-sandbox-s3-provider"
            recovery_bucket_name = helpers.recovery_bucket_name
            excluded_filetype = []
            name_1 = uuid.uuid4().__str__() + ".hdf"  # refers to file1.hdf
            key_name_1 = "test/" + uuid.uuid4().__str__() + "/" + name_1
            # Upload the randomized file to source bucket
            boto3.client('s3').upload_file(
                "file1.hdf", cumulus_bucket_name, key_name_1
            )
            name_2 = uuid.uuid4().__str__() + ".hdf"  # refers to file1.hdf
            key_name_2 = "test/" + uuid.uuid4().__str__() + "/" + name_2
            # Upload the randomized file to source bucket
            boto3.client('s3').upload_file(
                "file1.hdf", cumulus_bucket_name, key_name_2
            )
            execution_id_1 = uuid.uuid4().__str__()
            execution_id_2 = uuid.uuid4().__str__()

            copy_to_archive_input = {
                "payload": {
                    "granules": [
                        {
                            "granuleId": granule_id,
                            "createdAt": createdAt_time,
                            "files": [
                                {
                                    "bucket": cumulus_bucket_name,
                                    "key": key_name_1,
                                }
                            ]
                        },
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
                        "name": collection_name_1,
                        "version": collection_version_1
                    }
                },
                "cumulus_meta": {
                    "execution_name": execution_id_1
                }
            }

            expected_output = {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "createdAt": createdAt_time,
                        "files": [
                            {
                                "bucket": cumulus_bucket_name,
                                "key": key_name_1,
                            }
                        ]
                    },
                ],
                "copied_to_orca": [
                    "s3://" + cumulus_bucket_name + "/" + key_name_1,
                ]
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
            self.assertEqual(
                expected_output,
                json.loads(step_function_results["output"]),
                "Expected step function output not returned.",
            )

            copy_to_archive_input = {
                "payload": {
                    "granules": [
                        {
                            "granuleId": granule_id,
                            "createdAt": createdAt_time,
                            "files": [
                                {
                                    "bucket": cumulus_bucket_name,
                                    "key": key_name_2,
                                }
                            ]
                        },
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
                        "name": collection_name_2,
                        "version": collection_version_2
                    }
                },
                "cumulus_meta": {
                    "execution_name": execution_id_2
                }
            }

            expected_output = {
                "granules": [
                    {
                        "granuleId": granule_id,
                        "createdAt": createdAt_time,
                        "files": [
                            {
                                "bucket": cumulus_bucket_name,
                                "key": key_name_2,
                            }
                        ]
                    },
                ],
                "copied_to_orca": [
                    "s3://" + cumulus_bucket_name + "/" + key_name_2,
                ]
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
            self.assertEqual(
                expected_output,
                json.loads(step_function_results["output"]),
                "Expected step function output not returned.",
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
                logging.error(ex)
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
                        "collectionId": [
                            collection_name_1 + "___" + collection_version_1,
                            collection_name_2 + "___" + collection_version_2,
                        ],
                        "granuleId": [
                            granule_id,
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
                "collectionId": collection_name_1 + "___" + collection_version_1,
                "id": granule_id,
                "createdAt": createdAt_time,
                "executionId": execution_id_1,
                "files": [
                    {
                        "name": name_1,
                        "cumulusArchiveLocation": cumulus_bucket_name,
                        "orcaArchiveLocation": recovery_bucket_name,
                        "keyPath": key_name_1,
                        "sizeBytes": 6,
                        "hash": None, "hashType": None,
                        "storageClass": "GLACIER",
                        "version": s3_versions[0],
                    }
                ],
                "ingestDate": mock.ANY,
                "lastUpdate": mock.ANY
            },
                {
                    "providerId": provider_id,
                    "collectionId": collection_name_2 + "___" + collection_version_2,
                    "id": granule_id,
                    "createdAt": createdAt_time,
                    "executionId": execution_id_2,
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
                "Expected API output not returned."
            )
        except Exception as ex:
            logging.error(ex)
            raise
