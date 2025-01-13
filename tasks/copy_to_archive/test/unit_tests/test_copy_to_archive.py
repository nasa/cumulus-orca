import copy
import json
import os
import random
import unittest
import uuid
from test.unit_tests.ConfigCheck import ConfigCheck
from unittest import TestCase
from unittest.mock import ANY, MagicMock, Mock, call, patch

import boto3

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema
from boto3.s3.transfer import MB

# noinspection PyPackageRequirements
from moto import mock_sqs

import copy_to_archive
import sqs_library
from copy_to_archive import (
    CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY,
    CONFIG_MULTIPART_CHUNKSIZE_MB_KEY,
    should_exclude_files_type,
    task,
)

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestCopyToArchive(TestCase):
    """
    Test copy_to_archive functionality and business logic.
    """

    # Create the mock for SQS unit tests
    mock_sqs = mock_sqs()

    excluded_file = "s3://test-bucket/this_file_should_be_exclude.example"
    not_excluded_file = "s3://test-bucket/prefix/this_file_should_not_be_exclude.txt"
    two_prefix_file = "s3://test-bucket/prefix1/prefix2/file.txt"
    path_to_this_file = os.path.abspath(os.path.dirname(__file__))
    event_path = os.path.join(path_to_this_file, "event.json")
    event_granules = {
        "granules": [
            {
                "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
                "dataType": "MOD09GQ",
                "version": "006",
                "createdAt": 628021800000,
                "files": [
                    {
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318361000,
                        copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-protected",
                        "url_path": "MOD09GQ/006/",
                        "type": "",
                        copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",  # noqa: E501
                        "duplicate_found": True,
                        "checksumType": "md5",
                        "checksum": "bogus_checksum_value",
                    },
                    {
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318366000,
                        copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-private",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",  # noqa: E501
                        "duplicate_found": True,
                        "checksumType": "md5",
                        "checksum": "bogus_checksum_value",
                    },
                    {
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318372000,
                        copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-public",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",  # noqa: E501
                        "duplicate_found": True,
                        "checksumType": "md5",
                        "checksum": "bogus_checksum_value",
                    },
                    {
                        copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-private",
                        "type": "metadata",
                        copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",  # noqa: E501
                        "url_path": "MOD09GQ/006",
                        "checksumType": "md5",
                        "checksum": "bogus_checksum_value",
                    },
                ],
            }
        ]
    }

    def setUp(self):
        """
        Perform initial setup for the tests.
        """
        self.mock_sqs.start()
        self.test_sqs = boto3.resource("sqs", region_name="us-west-2")
        self.queue = self.test_sqs.create_queue(
            QueueName="test-metadata-queue.fifo", Attributes={"FifoQueue": "true"}
        )
        self.metadata_queue_url = self.queue.url

    def tearDown(self):
        """
        Perform teardown for the tests
        """
        self.mock_sqs.stop()

    @patch("copy_to_archive.LOGGER.info")
    def test_set_optional_event_property(
        self,
        mock_logger: MagicMock,
    ):
        """
        Tests that set_optional_event_property sets asyncOperationId as the value
        present in event and sets null value for other keys that are not present in event.
        """
        key0 = uuid.uuid4().__str__()  # no value, default to None
        key1 = uuid.uuid4().__str__()  # value present, set value in event
        key1_value = uuid.uuid4().__str__()
        key2 = uuid.uuid4().__str__()  # value present, override value in event
        key2_value = uuid.uuid4().__str__()
        mock_event = {
            "event": {
                "cumulus_meta": {"asyncOperationId": key2_value},
                "meta": {
                    "collection": {
                        "meta": {"orca": {"defaultBucketOverride": key1_value}}
                    }
                },
            },
            "config1": {key2: uuid.uuid4().__str__()},
        }
        mock_target_path_cursor = {
            "config0": {
                key0: "event.meta.collection.meta.orca.defaultRecoveryTypeOverride",
                key1: "event.meta.collection.meta.orca.defaultBucketOverride",
            },
            "config1": {key2: "event.cumulus_meta.asyncOperationId"},
        }
        copy_to_archive.set_optional_event_property(
            mock_event, mock_target_path_cursor, []
        )

        # set asyncOperationId to non-null value
        self.assertEqual(None, mock_event["config0"][key0])
        self.assertEqual(key1_value, mock_event["config0"][key1])
        self.assertEqual(key2_value, mock_event["config1"][key2])

    @patch("copy_to_archive.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "dataType": uuid.uuid4().__str__(),
                "version": uuid.uuid4().__str__(),
                "createdAt": random.randint(0, 628021800000),  # nosec
                "files": [
                    {
                        copy_to_archive.FILE_BUCKET_KEY: uuid.uuid4().__str__(),
                        copy_to_archive.FILE_FILEPATH_KEY: uuid.uuid4().__str__(),
                        copy_to_archive.FILE_HASH_KEY: uuid.uuid4().__str__(),
                        copy_to_archive.FILE_HASH_TYPE_KEY: uuid.uuid4().__str__(),
                    }
                ],
            }
        ]

        handler_input_event = {
            copy_to_archive.EVENT_INPUT_KEY: {"granules": granules},
            copy_to_archive.EVENT_CONFIG_KEY: {
                CONFIG_EXCLUDED_FILE_EXTENSIONS_KEY: [".png"],
                CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: 15,
                "providerId": uuid.uuid4().__str__(),
                "providerName": uuid.uuid4().__str__(),
                "executionId": uuid.uuid4().__str__(),
                "collectionShortname": "MOD09GQ",
                "collectionVersion": uuid.uuid4().__str__(),
            },
        }
        handler_input_context = Mock()

        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": uuid.uuid4().__str__(),
                    "files": [
                        {
                            copy_to_archive.FILE_BUCKET_KEY: uuid.uuid4().__str__(),
                            copy_to_archive.FILE_FILEPATH_KEY: uuid.uuid4().__str__(),
                        }
                    ],
                }
            ],
            "copied_to_orca": [uuid.uuid4().__str__()],
        }

        result = copy_to_archive.handler(handler_input_event, handler_input_context)
        mock_task.assert_called_once_with(
            handler_input_event[copy_to_archive.EVENT_INPUT_KEY],
            handler_input_event[copy_to_archive.EVENT_CONFIG_KEY],
        )

        self.assertEqual(mock_task.return_value, result)

    def test_exclude_file_types_excluded(self):
        """
        Testing exclude file types to be excluded
        """
        excluded_flag = should_exclude_files_type(self.excluded_file, [".example"])
        self.assertEqual(excluded_flag, True)

    def test_excluded_file_types_not_excluded(self):
        """
        Testing exclude file types not to be excluded
        """

        not_excluded_flag = should_exclude_files_type(
            self.not_excluded_file, [".example"]
        )
        self.assertEqual(not_excluded_flag, False)

    # todo: patch copy_granule_between_buckets here and elsewhere.
    # todo: Remove mock.ANY where possible. Currently used to ignore differences between files.
    @patch("copy_to_archive.get_storage_class")
    @patch("copy_to_archive.get_destination_bucket_name")
    @patch("copy_to_archive.sqs_library.post_to_metadata_queue")
    @patch.dict(
        os.environ,
        {
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
            "METADATA_DB_QUEUE_URL": "test",
            "AWS_REGION": "us-west-2",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_POOL_CONNECTIONS_KEY: "10",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_CONCURRENCY_KEY: "10",
        },
        clear=True,
    )
    def test_task_happy_path(
        self,
        mock_post_to_queue: MagicMock,
        mock_get_destination_bucket_name: MagicMock,
        mock_get_storage_class: MagicMock,
    ):
        """
        Basic path with buckets present.
        """
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [
            file[copy_to_archive.FILE_BUCKET_KEY]
            for file in self.event_granules["granules"][0]["files"]
        ]
        source_keys = [
            file[copy_to_archive.FILE_FILEPATH_KEY]
            for file in self.event_granules["granules"][0]["files"]
        ]

        config_check = ConfigCheck(4 * MB)

        # todo: use 'side_effect' to verify args.
        # It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.copy.side_effect = config_check.check_multipart_chunksize
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})
        file_return_value = {
            "Versions": [
                {
                    "ETag": '"8d1ff728a961869c715b458fa5f041f0"',
                    "Size": 14191,
                    "Key": "test/test.docx",
                    "VersionId": "1",
                    "IsLatest": True,
                }
            ]
        }
        s3_cli.list_object_versions = Mock(return_value=file_return_value)
        provider_id = uuid.uuid4().__str__()
        provider_name = uuid.uuid4().__str__()
        event_config = {
            "providerId": provider_id,
            "providerName": provider_name,
            "executionId": "test-execution-id",
            "collectionShortname": "MOD09GQ",
            "collectionVersion": uuid.uuid4().__str__(),
        }

        event_input = copy.deepcopy(self.event_granules)
        result = task(copy.deepcopy(event_input), copy.deepcopy(event_config))

        mock_get_destination_bucket_name.assert_called_once_with(event_config)
        mock_get_storage_class.assert_called_once_with(event_config)

        _OUTPUT_VALIDATE(result)

        expected_granules = copy.deepcopy(event_input["granules"])
        self.assertEqual(expected_granules, result["granules"])

        head_object_calls = []
        copy_calls = []
        for i in range(0, len(source_bucket_names)):
            head_object_calls.append(
                call(Bucket=source_bucket_names[i], Key=source_keys[i])
            )
            copy_calls.append(
                call(
                    {"Bucket": source_bucket_names[i], "Key": source_keys[i]},
                    mock_get_destination_bucket_name.return_value,
                    source_keys[i],
                    ExtraArgs={
                        "StorageClass": mock_get_storage_class.return_value,
                        "MetadataDirective": "COPY",
                        "ContentType": content_type,
                    },
                    Config=unittest.mock.ANY,  # Checked by ConfigCheck.
                    # Equality checkers do not work.
                )
            )

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)
        sqs_body = {
            "provider": {
                "name": provider_name,
                "providerId": event_config["providerId"],
            },
            "collection": {
                "shortname": event_config["collectionShortname"],
                "version": event_config["collectionVersion"],
                "collectionId": event_config["collectionShortname"]
                + "___"
                + event_config["collectionVersion"],
            },
            "granule": {
                "cumulusGranuleId": event_input["granules"][0]["granuleId"],
                "cumulusCreateTime": "1989-11-25T18:30:00+00:00",
                "executionId": event_config["executionId"],
                "ingestTime": ANY,
                "lastUpdate": ANY,
                "files": [
                    {
                        "cumulusArchiveLocation": event_input["granules"][0]["files"][
                            0
                        ]["bucket"],
                        "orcaArchiveLocation": mock_get_destination_bucket_name.return_value,
                        "keyPath": event_input["granules"][0]["files"][0][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ],
                        "sizeInBytes": ANY,
                        "version": ANY,
                        "ingestTime": ANY,
                        "etag": ANY,
                        "name": event_input["granules"][0]["files"][0][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ].split("/")[-1],
                        "hash": event_input["granules"][0]["files"][0][
                            copy_to_archive.FILE_HASH_KEY
                        ],
                        "hashType": event_input["granules"][0]["files"][0][
                            copy_to_archive.FILE_HASH_TYPE_KEY
                        ],
                        "storageClass": mock_get_storage_class.return_value,
                    },
                    {
                        "cumulusArchiveLocation": event_input["granules"][0]["files"][
                            1
                        ]["bucket"],
                        "orcaArchiveLocation": mock_get_destination_bucket_name.return_value,
                        "keyPath": event_input["granules"][0]["files"][1][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ],
                        "sizeInBytes": ANY,
                        "version": ANY,
                        "ingestTime": ANY,
                        "etag": ANY,
                        "name": event_input["granules"][0]["files"][1][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ].split("/")[-1],
                        "hash": event_input["granules"][0]["files"][1][
                            copy_to_archive.FILE_HASH_KEY
                        ],
                        "hashType": event_input["granules"][0]["files"][1][
                            copy_to_archive.FILE_HASH_TYPE_KEY
                        ],
                        "storageClass": mock_get_storage_class.return_value,
                    },
                    {
                        "cumulusArchiveLocation": event_input["granules"][0]["files"][
                            2
                        ]["bucket"],
                        "orcaArchiveLocation": mock_get_destination_bucket_name.return_value,
                        "keyPath": event_input["granules"][0]["files"][2][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ],
                        "sizeInBytes": ANY,
                        "version": ANY,
                        "ingestTime": ANY,
                        "etag": ANY,
                        "name": event_input["granules"][0]["files"][2][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ].split("/")[-1],
                        "hash": event_input["granules"][0]["files"][2][
                            copy_to_archive.FILE_HASH_KEY
                        ],
                        "hashType": event_input["granules"][0]["files"][2][
                            copy_to_archive.FILE_HASH_TYPE_KEY
                        ],
                        "storageClass": mock_get_storage_class.return_value,
                    },
                    {
                        "cumulusArchiveLocation": event_input["granules"][0]["files"][
                            3
                        ]["bucket"],
                        "orcaArchiveLocation": mock_get_destination_bucket_name.return_value,
                        "keyPath": event_input["granules"][0]["files"][3][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ],
                        "sizeInBytes": ANY,
                        "version": ANY,
                        "ingestTime": ANY,
                        "etag": ANY,
                        "name": event_input["granules"][0]["files"][0][
                            copy_to_archive.FILE_FILEPATH_KEY
                        ].split("/")[-1],
                        "hash": event_input["granules"][0]["files"][3][
                            copy_to_archive.FILE_HASH_KEY
                        ],
                        "hashType": event_input["granules"][0]["files"][3][
                            copy_to_archive.FILE_HASH_TYPE_KEY
                        ],
                        "storageClass": mock_get_storage_class.return_value,
                    },
                ],
            },
        }

        mock_post_to_queue.assert_called_once_with(
            sqs_body, os.environ["METADATA_DB_QUEUE_URL"]
        )

        self.assertEqual(s3_cli.head_object.call_count, 4)
        self.assertEqual(s3_cli.copy.call_count, 4)
        self.assertEqual(s3_cli.list_object_versions.call_count, 4)

        expected_copied_file_urls = [
            f"s3://{file[copy_to_archive.FILE_BUCKET_KEY]}/"
            f"{file[copy_to_archive.FILE_FILEPATH_KEY]}"
            for file in self.event_granules["granules"][0]["files"]
        ]
        self.assertEqual(expected_copied_file_urls, result["copied_to_orca"])
        expected_granules = copy.deepcopy(event_input["granules"])
        self.assertEqual(expected_granules, result["granules"])
        self.assertIsNone(config_check.bad_config)

    @patch("copy_to_archive.get_storage_class")
    @patch("copy_to_archive.get_destination_bucket_name")
    @patch("copy_to_archive.sqs_library.post_to_metadata_queue")
    @patch.dict(
        os.environ,
        {
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
            "METADATA_DB_QUEUE_URL": "test",
            "AWS_REGION": "us-west-2",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_POOL_CONNECTIONS_KEY: "10",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_CONCURRENCY_KEY: "10",
        },
        clear=True,
    )
    def test_task_happy_path_multiple_granules(
        self,
        mock_post_to_queue: MagicMock,
        mock_get_destination_bucket_name: MagicMock,
        mock_get_storage_class: MagicMock,
    ):
        """
        Happy path for multiple granules in input.
        """
        multiple_event_granules = {
            "granules": [
                {
                    "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
                    "dataType": "MOD09GQ",
                    "version": "006",
                    "createdAt": random.randint(0, 628021800000),  # nosec
                    "files": [
                        {
                            "path": "MOD09GQ/006",
                            "size": 6,
                            "time": 1608318361000,
                            copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-protected",
                            "url_path": "MOD09GQ/006/",
                            "type": "",
                            copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",  # noqa: E501
                            "duplicate_found": True,
                            copy_to_archive.FILE_HASH_TYPE_KEY: "md5",
                            copy_to_archive.FILE_HASH_KEY: "bogus_checksum_value",
                        },
                    ],
                },
                {
                    "granuleId": "MOD09GQ.A208885.h21v00.006.2017034065108",
                    "dataType": "MOD09GQ",
                    "version": "008",
                    "createdAt": random.randint(0, 628021800000),  # nosec
                    "files": [
                        {
                            "path": "MOD09GQ/006",
                            "size": 7,
                            "time": 1608318361000,
                            copy_to_archive.FILE_BUCKET_KEY: "orca-sandbox-protected",
                            "url_path": "MOD09GQ/006/",
                            "type": "",
                            copy_to_archive.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065108.hdf",  # noqa: E501
                            "duplicate_found": True,
                            copy_to_archive.FILE_HASH_TYPE_KEY: "md5",
                            copy_to_archive.FILE_HASH_KEY: "bogus_checksum_value",
                        },
                    ],
                },
            ]
        }
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [
            file[copy_to_archive.FILE_BUCKET_KEY]
            for file in multiple_event_granules["granules"][0]["files"]
        ]
        source_keys = [
            file[copy_to_archive.FILE_FILEPATH_KEY]
            for file in multiple_event_granules["granules"][0]["files"]
        ]

        config_check = ConfigCheck(4 * MB)

        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.copy.side_effect = config_check.check_multipart_chunksize
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})
        file_return_value = {
            "Versions": [
                {
                    "ETag": '"8d1ff728a961869c715b458fa5f041f0"',
                    "Size": 14191,
                    "Key": "test/test.docx",
                    "VersionId": "1",
                    "IsLatest": True,
                }
            ]
        }
        provider_id = uuid.uuid4().__str__()
        s3_cli.list_object_versions = Mock(return_value=file_return_value)
        event_config = {
            "providerId": provider_id,
            "executionId": "test-execution-id",
            "collectionShortname": "MOD09GQ",
            "collectionVersion": uuid.uuid4().__str__(),
        }
        event_input = copy.deepcopy(multiple_event_granules)

        result = task(copy.deepcopy(event_input), copy.deepcopy(event_config))

        mock_get_destination_bucket_name.assert_called_once_with(event_config)
        mock_get_storage_class.assert_called_once_with(event_config)

        _OUTPUT_VALIDATE(result)

        expected_granules = copy.deepcopy(event_input["granules"])
        self.assertEqual(expected_granules, result["granules"])

        head_object_calls = []
        copy_calls = []
        for i in range(0, len(source_bucket_names)):
            head_object_calls.append(
                call(Bucket=source_bucket_names[i], Key=source_keys[i])
            )
            copy_calls.append(
                call(
                    {"Bucket": source_bucket_names[i], "Key": source_keys[i]},
                    mock_get_destination_bucket_name.return_value,
                    source_keys[i],
                    ExtraArgs={
                        "StorageClass": mock_get_storage_class.return_value,
                        "MetadataDirective": "COPY",
                        "ContentType": content_type,
                    },
                    Config=unittest.mock.ANY,  # Checked by ConfigCheck.
                    # Equality checkers do not work.
                )
            )

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)
        self.assertEqual(mock_post_to_queue.call_count, 2)  # todo: Add proper checks.
        self.assertEqual(s3_cli.head_object.call_count, 2)
        self.assertEqual(s3_cli.copy.call_count, 2)
        self.assertEqual(s3_cli.list_object_versions.call_count, 2)
        self.assertEqual(multiple_event_granules["granules"], result["granules"])

    @patch("copy_to_archive.get_storage_class")
    @patch("copy_to_archive.get_destination_bucket_name")
    @patch("copy_to_archive.sqs_library.post_to_metadata_queue")
    @patch.dict(
        os.environ,
        {
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
            "METADATA_DB_QUEUE_URL": "test",
            "AWS_REGION": "us-west-2",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_POOL_CONNECTIONS_KEY: "10",
            copy_to_archive.OS_ENVIRON_DEFAULT_MAX_CONCURRENCY_KEY: "10",
        },
        clear=True,
    )
    def test_task_overridden_multipart_chunksize(
        self,
        mock_post_to_queue: MagicMock,  # todo: Add proper checks
        mock_get_destination_bucket_name: MagicMock,
        mock_get_storage_class: MagicMock,
    ):
        """
        If the collection has a different multipart chunksize, it should override the default.
        """
        overridden_multipart_chunksize_mb = 5
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [
            file[copy_to_archive.FILE_BUCKET_KEY]
            for file in self.event_granules["granules"][0]["files"]
        ]
        source_keys = [
            file[copy_to_archive.FILE_FILEPATH_KEY]
            for file in self.event_granules["granules"][0]["files"]
        ]

        config_check = ConfigCheck(overridden_multipart_chunksize_mb * MB)

        # todo: use 'side_effect' to verify args.
        # It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.copy.side_effect = config_check.check_multipart_chunksize
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})
        file_return_value = {
            "Versions": [
                {
                    "ETag": '"8d1ff728a961869c715b458fa5f041f0"',
                    "Size": 14191,
                    "Key": "test/test.docx",
                    "VersionId": "1",
                    "IsLatest": True,
                }
            ]
        }
        s3_cli.list_object_versions = Mock(return_value=file_return_value)
        provider_id = uuid.uuid4().__str__()
        event_config = {
            CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: str(overridden_multipart_chunksize_mb),
            "providerId": provider_id,
            "executionId": "test-execution-id",
            "collectionShortname": "MOD09GQ",
            "collectionVersion": uuid.uuid4().__str__(),
        }
        event_input = copy.deepcopy(self.event_granules)

        result = task(copy.deepcopy(event_input), event_config)

        mock_get_destination_bucket_name.assert_called_once_with(event_config)
        mock_get_storage_class.assert_called_once_with(event_config)

        _OUTPUT_VALIDATE(result)

        expected_granules = copy.deepcopy(event_input["granules"])
        self.assertEqual(expected_granules, result["granules"])

        head_object_calls = []
        copy_calls = []
        for i in range(0, len(source_bucket_names)):
            head_object_calls.append(
                call(Bucket=source_bucket_names[i], Key=source_keys[i])
            )
            copy_calls.append(
                call(
                    {"Bucket": source_bucket_names[i], "Key": source_keys[i]},
                    mock_get_destination_bucket_name.return_value,
                    source_keys[i],
                    ExtraArgs={
                        "StorageClass": mock_get_storage_class.return_value,
                        "MetadataDirective": "COPY",
                        "ContentType": content_type,
                    },
                    Config=unittest.mock.ANY,  # Checked by ConfigCheck.
                    # Equality checkers do not work.
                )
            )

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)

        self.assertEqual(s3_cli.head_object.call_count, 4)
        self.assertEqual(s3_cli.copy.call_count, 4)
        self.assertEqual(s3_cli.list_object_versions.call_count, 4)
        expected_copied_file_urls = [
            f"s3://{file[copy_to_archive.FILE_BUCKET_KEY]}/"
            f"{file[copy_to_archive.FILE_FILEPATH_KEY]}"
            for file in self.event_granules["granules"][0]["files"]
        ]
        self.assertEqual(expected_copied_file_urls, result["copied_to_orca"])
        expected_granules = copy.deepcopy(event_input["granules"])
        self.assertEqual(expected_granules, result["granules"])
        self.assertIsNone(config_check.bad_config)

    @patch("copy_to_archive.get_storage_class")
    @patch("copy_to_archive.get_destination_bucket_name")
    @patch.dict(
        os.environ,
        {"DEFAULT_MULTIPART_CHUNKSIZE_MB": "4", "METADATA_DB_QUEUE_URL": "test"},
        clear=True,
    )
    def test_task_empty_granules_list(
        self,
        mock_get_destination_bucket_name: MagicMock,
        mock_get_storage_class: MagicMock,
    ):
        """
        Basic path with buckets present.
        """
        # todo: use 'side_effect' to verify args.
        # It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock()
        s3_cli.head_object = Mock()

        provider_id = uuid.uuid4().__str__()
        config = {
            "providerId": provider_id,
            "executionId": "test-execution-id",
            "collectionShortname": "MOD09GQ",
            "collectionVersion": uuid.uuid4().__str__(),
        }

        result = task({"granules": []}, copy.deepcopy(config))

        mock_get_destination_bucket_name.assert_called_once_with(config)
        mock_get_storage_class.assert_called_once_with(config)

        _OUTPUT_VALIDATE(result)

        self.assertEqual([], result["granules"])
        granules = result["granules"]
        self.assertEqual(0, len(granules))

        s3_cli.head_object.assert_not_called()
        s3_cli.copy.assert_not_called()

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_destination_bucket_name_returns_override_if_present(self):
        bucket = Mock()
        result = copy_to_archive.get_destination_bucket_name(
            {copy_to_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: bucket}
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_destination_bucket_name_returns_default_if_override_is_null(
        self,
    ):
        bucket = os.environ[copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY]
        result = copy_to_archive.get_destination_bucket_name(
            {copy_to_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: None}
        )
        self.assertEqual(bucket, result)

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_destination_bucket_name_returns_default_if_override_not_given(self):
        bucket = os.environ[copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY]
        result = copy_to_archive.get_destination_bucket_name({})
        self.assertEqual(bucket, result)

    def test_get_destination_bucket_name_no_result_raises_error(self):
        with self.assertRaises(KeyError) as cm:
            copy_to_archive.get_destination_bucket_name(
                {copy_to_archive.CONFIG_DEFAULT_BUCKET_OVERRIDE_KEY: None}
            )
        self.assertEqual(
            f"'{copy_to_archive.OS_ENVIRON_ORCA_DEFAULT_BUCKET_KEY} "
            f"environment variable is not set.'",
            str(cm.exception),
        )

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_storage_class_returns_override_if_present(self):
        storage_class = Mock()
        result = copy_to_archive.get_storage_class(
            {copy_to_archive.CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY: storage_class}
        )
        self.assertEqual(storage_class, result)

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_storage_class_returns_default_if_override_is_null(
        self,
    ):
        storage_class = os.environ[copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY]
        result = copy_to_archive.get_storage_class(
            {copy_to_archive.CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY: None}
        )
        self.assertEqual(storage_class, result)

    @patch.dict(
        os.environ,
        {copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY: uuid.uuid4().__str__()},
        clear=True,
    )
    def test_get_storage_class_returns_default_if_override_not_given(self):
        storage_class = os.environ[copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY]
        result = copy_to_archive.get_storage_class({})
        self.assertEqual(storage_class, result)

    def test_get_storage_class_no_result_raises_error(self):
        with self.assertRaises(KeyError) as cm:
            copy_to_archive.get_storage_class(
                {copy_to_archive.CONFIG_DEFAULT_STORAGE_CLASS_OVERRIDE_KEY: None}
            )
        self.assertEqual(
            f"'{copy_to_archive.OS_ENVIRON_DEFAULT_STORAGE_CLASS_KEY} "
            f"environment variable is not set.'",
            str(cm.exception),
        )

    @patch("time.sleep")
    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"}, clear=True)
    def test_post_to_metadata_queue_happy_path(self, mock_sleep: MagicMock):
        """
        SQS library happy path. Checks that the message sent to SQS
        is same as the message received from SQS.
        """
        sqs_body = {
            "provider": {"providerId": "1234", "name": "LPCumulus"},
            "collection": {
                "collectionId": "MOD14A1__061",
                "shortname": "MOD14A1",
                "version": "061",
            },
            "granule": {
                "cumulusGranuleId": "MOD14A1.061.A23V45.2020235",
                "cumulusCreateTime": "2019-07-17T17:36:38.494918+00:00",
                "executionId": "f2fgh-356-789",
                "ingestTime": "2019-07-17T17:36:38.494918+00:00",
                "lastUpdate": "2019-07-17T17:36:38.494918+00:00",
                "files": [
                    {
                        "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                        "cumulusArchiveLocation": "cumulus-archive",
                        "orcaArchiveLocation": "orca-archive",
                        "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                        "sizeInBytes": 100934568723,
                        "hash": "ACFH325128030192834127347",
                        "hashType": "SHA-256",
                        "storageClass": "DEEP_ARCHIVE",
                        "version": "VXCDEG902",
                        "ingestTime": "2019-07-17T17:36:38.494918+00:00",
                        "etag": "YXC432BGT789",
                    }
                ],
            },
        }
        # Send values to the function
        sqs_library.post_to_metadata_queue(
            sqs_body,
            self.metadata_queue_url,
        )
        # grabbing queue contents after the message is sent
        queue_contents = self.queue.receive_messages()
        queue_output_body = json.loads(queue_contents[0].body)

        # Testing required fields
        self.assertEqual(queue_output_body, sqs_body)

        mock_sleep.assert_not_called()

    # Todo: since sleep is not called in function under test,
    # this violates good unit test practices. Fix in ORCA-406
    @patch("time.sleep")
    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"}, clear=True)
    def test_post_to_metadata_queue_retry_failures(self, mock_sleep: MagicMock):
        """
        Produces a failure and checks if retries are performed in the SQS library.
        """
        sqs_body = {
            "provider": {"providerId": "1234", "name": "LPCumulus"},
            "collection": {
                "collectionId": "MOD14A1__061",
                "shortname": "MOD14A1",
                "version": "061",
            },
            "granule": {
                "cumulusGranuleId": "MOD14A1.061.A23V45.2020235",
                "cumulusCreateTime": "2019-07-17T17:36:38.494918+00:00",
                "executionId": "f2fgh-356-789",
                "ingestTime": "2019-07-17T17:36:38.494918+00:00",
                "lastUpdate": "2019-07-17T17:36:38.494918+00:00",
                "files": [
                    {
                        "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                        "cumulusArchiveLocation": "cumulus-archive",
                        "orcaArchiveLocation": "orca-archive",
                        "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                        "sizeInBytes": 100934568723,
                        "hash": "ACFH325128030192834127347",
                        "hashType": "SHA-256",
                        "storageClass": "DEEP_ARCHIVE",
                        "version": "VXCDEG902",
                        "ingestTime": "2019-07-17T17:36:38.494918+00:00",
                        "etag": "YXC432BGT789",
                    }
                ],
            },
        }
        # url is intentionally set wrong so send_message will fail.
        # Send values to the function
        with self.assertRaises(Exception) as cm:
            sqs_library.post_to_metadata_queue(
                sqs_body,
                "dummy",
            )
        self.assertEqual(
            "An error occurred (AWS.SimpleQueueService.NonExistentQueue) when calling the "
            "SendMessage operation: The specified queue does not exist for this wsdl version.",
            str(cm.exception),
        )
        self.assertEqual(3, mock_sleep.call_count)


# TODO: Write tests to validate file name regex exclusion

# todo: switch this to large test
#    def test_5_task(self):
#        """
#        Testing task
#        """
#        context = []
#        with open(self.event_path) as f:
#            event = json.load(f)
#            test_handler = task(event, context)
#            print(test_handler)
#
