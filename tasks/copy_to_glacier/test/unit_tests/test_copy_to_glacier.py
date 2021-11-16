import copy
import json
import unittest
import uuid
from unittest import TestCase
from unittest.mock import Mock, call, patch, MagicMock
import fastjsonschema as fastjsonschema

import copy_to_glacier
import sqs_library
from copy_to_glacier import *
from test.helpers import LambdaContextMock
from test.unit_tests.ConfigCheck import ConfigCheck
from moto import mock_sqs


class TestCopyToGlacierHandler(TestCase):
    """
    Test copy to glacier handler
    This will test if the function of test copy to glacier work as expected
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
                "files": [
                    {
                        copy_to_glacier.FILE_FILENAME_KEY: "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318361000,
                        copy_to_glacier.FILE_BUCKET_KEY: "orca-sandbox-protected",
                        "url_path": "MOD09GQ/006/",
                        "type": "",
                        copy_to_glacier.FILE_SOURCE_URI_KEY: "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        copy_to_glacier.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        "duplicate_found": True,
                    },
                    {
                        copy_to_glacier.FILE_FILENAME_KEY: "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318366000,
                        copy_to_glacier.FILE_BUCKET_KEY: "orca-sandbox-private",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        copy_to_glacier.FILE_SOURCE_URI_KEY: "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        copy_to_glacier.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        "duplicate_found": True,
                    },
                    {
                        copy_to_glacier.FILE_FILENAME_KEY: "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318372000,
                        copy_to_glacier.FILE_BUCKET_KEY: "orca-sandbox-public",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        copy_to_glacier.FILE_SOURCE_URI_KEY: "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        copy_to_glacier.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        "duplicate_found": True,
                    },
                    {
                        copy_to_glacier.FILE_FILENAME_KEY: "MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        copy_to_glacier.FILE_BUCKET_KEY: "orca-sandbox-private",
                        copy_to_glacier.FILE_SOURCE_URI_KEY: "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        "type": "metadata",
                        copy_to_glacier.FILE_FILEPATH_KEY: "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        "url_path": "MOD09GQ/006",
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
        self.queue = self.test_sqs.create_queue(QueueName="test-metadata-queue")
        self.metadata_queue_url = self.queue.url

    def tearDown(self):
        """
        Perform teardown for the tests
        """
        self.mock_sqs.stop()

    @patch("copy_to_glacier.task")
    def test_handler_happy_path(self, mock_task: MagicMock):
        granules = [
            {
                "granuleId": uuid.uuid4().__str__(),
                "files": [
                    {
                        copy_to_glacier.FILE_FILENAME_KEY: uuid.uuid4().__str__(),
                        copy_to_glacier.FILE_BUCKET_KEY: uuid.uuid4().__str__(),
                        copy_to_glacier.FILE_FILEPATH_KEY: uuid.uuid4().__str__(),
                        copy_to_glacier.FILE_SOURCE_URI_KEY: uuid.uuid4().__str__(),
                    }
                ],
            }
        ]

        handler_input_event = {
            "payload": {"granules": granules},
            "task_config": {
                CONFIG_EXCLUDE_FILE_TYPES_KEY: [".png"],
                CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: 15,
            },
        }
        handler_input_context = LambdaContextMock()

        expected_task_input = {
            "input": handler_input_event["payload"],
            "config": handler_input_event["task_config"],
        }
        mock_task.return_value = {
            "granules": [
                {
                    "granuleId": uuid.uuid4().__str__(),
                    "files": [
                        {
                            "name": uuid.uuid4().__str__(),
                            "bucket": uuid.uuid4().__str__(),
                            "filepath": uuid.uuid4().__str__(),
                            "filename": uuid.uuid4().__str__(),
                        }
                    ]
                }
            ],
            "copied_to_glacier": [uuid.uuid4().__str__()],
        }

        result = copy_to_glacier.handler(handler_input_event, handler_input_context)
        mock_task.assert_called_once_with(expected_task_input, handler_input_context)

        self.assertEqual(mock_task.return_value, result["payload"])

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

    @patch.dict(
        os.environ,
        {
            "ORCA_DEFAULT_BUCKET": uuid.uuid4().__str__(),
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
        },
        clear=True,
    )
    def test_task_happy_path(self):
        """
        Basic path with buckets present.
        """
        destination_bucket_name = os.environ["ORCA_DEFAULT_BUCKET"]
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [
            file[copy_to_glacier.FILE_BUCKET_KEY] for file in self.event_granules["granules"][0]["files"]
        ]
        source_keys = [
            file[copy_to_glacier.FILE_FILEPATH_KEY] for file in self.event_granules["granules"][0]["files"]
        ]

        config_check = ConfigCheck(4 * MB)

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.copy.side_effect = config_check.check_multipart_chunksize
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})

        event = {"input": copy.deepcopy(self.event_granules), "config": {}}

        result = task(copy.deepcopy(event), None)

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

        expected_granules = copy.deepcopy(event["input"]["granules"])
        for granule in expected_granules:
            for file in granule["files"]:
                copy_to_glacier.switch_file_to_output_format(file)
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
                    destination_bucket_name,
                    source_keys[i],
                    ExtraArgs={
                        "StorageClass": "GLACIER",
                        "MetadataDirective": "COPY",
                        "ContentType": content_type,
                        "ACL": "bucket-owner-full-control",
                    },
                    Config=unittest.mock.ANY,  # Checked by ConfigCheck. Equality checkers do not work.
                )
            )

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)

        self.assertEqual(s3_cli.head_object.call_count, 4)
        self.assertEqual(s3_cli.copy.call_count, 4)

        expected_copied_file_urls = [
            file[copy_to_glacier.FILE_SOURCE_URI_KEY] for file in self.event_granules["granules"][0]["files"]
        ]
        self.assertEqual(expected_copied_file_urls, result["copied_to_glacier"])
        expected_granules = copy.deepcopy(event["input"]["granules"])
        for granule in expected_granules:
            for file in granule["files"]:
                copy_to_glacier.switch_file_to_output_format(file)
        self.assertEqual(expected_granules, result["granules"])
        self.assertIsNone(config_check.bad_config)

    @patch.dict(
        os.environ,
        {
            "ORCA_DEFAULT_BUCKET": uuid.uuid4().__str__(),
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
        },
        clear=True,
    )
    def test_task_overridden_multipart_chunksize(self):
        """
        If the collection has a different multipart chunksize, it should override the default.
        """
        overridden_multipart_chunksize_mb = 5
        destination_bucket_name = os.environ["ORCA_DEFAULT_BUCKET"]
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [
            file[copy_to_glacier.FILE_BUCKET_KEY] for file in self.event_granules["granules"][0]["files"]
        ]
        source_keys = [
            file[copy_to_glacier.FILE_FILEPATH_KEY] for file in self.event_granules["granules"][0]["files"]
        ]

        config_check = ConfigCheck(overridden_multipart_chunksize_mb * MB)

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.copy.side_effect = config_check.check_multipart_chunksize
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})

        event = {
            "input": copy.deepcopy(self.event_granules),
            "config": {
                CONFIG_MULTIPART_CHUNKSIZE_MB_KEY: str(
                    overridden_multipart_chunksize_mb
                )
            },
        }

        result = task(copy.deepcopy(event), None)

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

        expected_granules = copy.deepcopy(event["input"]["granules"])
        for granule in expected_granules:
            for file in granule["files"]:
                copy_to_glacier.switch_file_to_output_format(file)
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
                    destination_bucket_name,
                    source_keys[i],
                    ExtraArgs={
                        "StorageClass": "GLACIER",
                        "MetadataDirective": "COPY",
                        "ContentType": content_type,
                        "ACL": "bucket-owner-full-control",
                    },
                    Config=unittest.mock.ANY,  # Checked by ConfigCheck. Equality checkers do not work.
                )
            )

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)

        self.assertEqual(s3_cli.head_object.call_count, 4)
        self.assertEqual(s3_cli.copy.call_count, 4)

        expected_copied_file_urls = [
            file[copy_to_glacier.FILE_SOURCE_URI_KEY] for file in self.event_granules["granules"][0]["files"]
        ]
        self.assertEqual(expected_copied_file_urls, result["copied_to_glacier"])
        expected_granules = copy.deepcopy(event["input"]["granules"])
        for granule in expected_granules:
            for file in granule["files"]:
                copy_to_glacier.switch_file_to_output_format(file)
        self.assertEqual(expected_granules, result["granules"])
        self.assertIsNone(config_check.bad_config)

    @patch.dict(
        os.environ,
        {
            "ORCA_DEFAULT_BUCKET": uuid.uuid4().__str__(),
            "DEFAULT_MULTIPART_CHUNKSIZE_MB": "4",
        },
        clear=True,
    )
    def test_task_empty_granules_list(self):
        """
        Basic path with buckets present.
        """
        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock()
        s3_cli.head_object = Mock()

        event = {"input": {"granules": []}, "config": {}}

        result = task(copy.deepcopy(event), None)

        with open("schemas/output.json", "r") as raw_schema:
            schema = json.loads(raw_schema.read())

        validate = fastjsonschema.compile(schema)
        validate(result)

        self.assertEqual([], result["granules"])
        granules = result["granules"]
        self.assertEqual(0, len(granules))

        s3_cli.head_object.assert_not_called()
        s3_cli.copy.assert_not_called()

    @patch.dict(os.environ, {"ORCA_DEFAULT_BUCKET": ""}, clear=True)
    def test_task_invalid_environment_variable(self):
        """
        Checks to make sure an unset or empty environment variable throws an error
        """
        content_type = uuid.uuid4().__str__()

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client("s3")
        s3_cli.copy = Mock(return_value=None)
        s3_cli.head_object = Mock(return_value={"ContentType": content_type})

        event = {"input": copy.deepcopy(self.event_granules), "config": {}}

        with self.assertRaises(KeyError) as context:
            task(copy.deepcopy(event), None)
            self.assertTrue(
                "ORCA_DEFAULT_BUCKET environment variable is not set."
                in context.exception
            )

    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"}, clear=True)
    def test_post_to_metadata_queue_happy_path(self):
        """
        SQS library happy path. Checks that the message sent to SQS is same as the message received from SQS.
        """
        sqs_body = {
            "provider": {"providerId": "1234", "name": "LPCUmumulus"},
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

    @patch("time.sleep")
    @patch("sqs_library.retry_error")
    @patch.dict(os.environ, {"AWS_REGION": "us-west-2"}, clear=True)
    def test_post_to_metadata_queue_retry_failures(
        self, mock_retry_error: MagicMock, mock_sleep: MagicMock
    ):
        """
        Produces a failure in the json schema and checks if retries are performed in the SQS library.
        """
        # collectionId is intentionally removed so the schema validation will fail.
        sqs_body = {
            "provider": {"providerId": "1234", "name": "LPCUmumulus"},
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
                        "version": "VXCDEG902",
                        "ingestTime": "2019-07-17T17:36:38.494918+00:00",
                        "etag": "YXC432BGT789",
                    }
                ],
            },
        }
        #
        self.metadata_queue_url = "dummy"
        # Send values to the function
        with self.assertRaises(Exception) as ex:
            sqs_library.post_to_metadata_queue(
                sqs_body,
                self.metadata_queue_url,
            )
        self.assertEqual(3, mock_sleep.call_count)


##TODO: Write tests to validate file name regex exclusion

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
