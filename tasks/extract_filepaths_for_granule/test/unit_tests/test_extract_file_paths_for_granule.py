"""
Name: test_extract_filepaths_for_granule.py

Description:  Unit tests for extract_file_paths_for_granule.py.
"""

import json
import unittest
import uuid
from test.helpers import create_handler_event, create_task_event
from unittest.mock import MagicMock, Mock, patch

import extract_filepaths_for_granule

# noinspection PyPackageRequirements
import fastjsonschema as fastjsonschema

# Generating schema validators can take time, so do it once and reuse.
with open("schemas/input.json", "r") as raw_schema:
    _INPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))
with open("schemas/output.json", "r") as raw_schema:
    _OUTPUT_VALIDATE = fastjsonschema.compile(json.loads(raw_schema.read()))


class TestExtractFilePaths(unittest.TestCase):
    """
    TestExtractFilePaths.
    """

    def setUp(self):
        self.task_input_event = create_task_event()
        self.granuleId = uuid.uuid4().__str__()
        self.collectionId = uuid.uuid4().__str__()
        self.input_bucket = "cumulus-test-sandbox-protected-2"
        self.protected_bucket = "sndbx-cumulus-protected"
        self.internal_bucket = "sndbx-cumulus-internal"
        self.private_bucket = "sndbx-cumulus-private"
        self.public_bucket = "sndbx-cumulus-public"
        self.sampleFileName1 = "L0A_HR_RAW_product_0010-of-0420"
        self.sampleFileName2 = "L0A_HR_RAW_product_0001-of-0019"

    @patch("extract_filepaths_for_granule.task")
    @patch("extract_filepaths_for_granule.set_optional_event_property")
    def test_handler_happy_path(
        self, mock_optional_property: MagicMock, mock_task: MagicMock
    ):
        """
        Tests happy path for lambda handler.
        """
        handler_input_event = create_handler_event()
        handler_input_event["config"] = {
            extract_filepaths_for_granule.CONFIG_FILE_BUCKETS_KEY: [
                {
                    "regex": ".*.h5$",
                    "sampleFileName": self.sampleFileName1 + ".h5",
                    "bucket": "protected",
                },
                {
                    "regex": ".*.cmr.xml$",
                    "sampleFileName": self.sampleFileName1 + ".iso.xml",
                    "bucket": "protected",
                },
                {
                    "regex": ".*.h5.mp$",
                    "sampleFileName": self.sampleFileName2 + ".h5.mp",
                    "bucket": "public",
                },
                {
                    "regex": ".*.cmr.json$",
                    "sampleFileName": self.sampleFileName2 + ".cmr.json",
                    "bucket": "public",
                },
            ],
            "buckets": {
                "protected": {"name": self.protected_bucket, "type": "protected"},
                "internal": {"name": self.internal_bucket, "type": "internal"},
                "private": {"name": self.private_bucket, "type": "private"},
                "public": {"name": self.public_bucket, "type": "public"},
            },
        }

        mock_task.return_value = {
            "granules": [
                {
                    "collectionId": self.collectionId,
                    "granuleId": self.granuleId,
                    "keys": [
                        self.granuleId + ".h5",
                        self.granuleId + ".cmr.json",
                    ],
                }
            ]
        }
        context = Mock()
        result = extract_filepaths_for_granule.handler(handler_input_event, context)

        mock_task.assert_called_once_with(
            handler_input_event["input"], handler_input_event["config"]
        )
        mock_optional_property.assert_called_once_with(handler_input_event, {}, [])
        self.assertEqual(mock_task.return_value, result)

    @patch("extract_filepaths_for_granule.task")
    @patch("extract_filepaths_for_granule.set_optional_event_property")
    def test_handler_raises_error_bad_config(self, _: MagicMock, mock_task: MagicMock):
        """
        Tests that expected error is raised on bad config such as missing regex key.
        """
        handler_input_event = create_handler_event()
        handler_input_event["config"] = {
            extract_filepaths_for_granule.CONFIG_FILE_BUCKETS_KEY: [
                {
                    "sampleFileName": self.sampleFileName1 + ".h5",
                    "bucket": "protected",
                },
                {
                    "sampleFileName": self.sampleFileName1 + ".iso.xml",
                    "bucket": "protected",
                },
                {
                    "sampleFileName": self.sampleFileName2 + ".h5.mp",
                    "bucket": "public",
                },
                {
                    "sampleFileName": self.sampleFileName2 + ".cmr.json",
                    "bucket": "public",
                },
            ],
            "buckets": {
                "protected": {"name": self.protected_bucket, "type": "protected"},
                "internal": {"name": self.internal_bucket, "type": "internal"},
                "private": {"name": self.private_bucket, "type": "private"},
                "public": {"name": self.public_bucket, "type": "public"},
            },
        }
        context = Mock()
        with self.assertRaises(Exception) as ex:
            extract_filepaths_for_granule.handler(handler_input_event, context)
        self.assertEqual(
            "data.fileBucketMaps[0] must contain " "['regex', 'bucket'] properties",
            str(ex.exception),
        )
        mock_task.assert_not_called()

    @patch("extract_filepaths_for_granule.task")
    @patch("extract_filepaths_for_granule.set_optional_event_property")
    def test_handler_raises_error_bad_input(self, _: MagicMock, mock_task: MagicMock):
        """
        Tests that expected error is raised on bad input such as missing granuleId.
        """
        bad_handler_input_event = {
            "input": {
                "granules": [
                    {
                        "collectionId": self.collectionId,
                        "status": "completed",
                        "files": [
                            {
                                "checksumType": "md5",
                                "bucket": self.internal_bucket,
                                "type": "data",
                                "fileName": self.sampleFileName1 + ".cmr.json",
                                "key": self.sampleFileName1 + ".cmr.json",
                                "size": 2154070040,
                            }
                        ],
                        "endingDateTime": "2015-09-25T23:29:57.000Z",
                    }
                ]
            },
            "config": Mock(),
        }
        context = Mock()
        with self.assertRaises(Exception) as ex:
            extract_filepaths_for_granule.handler(bad_handler_input_event, context)
        self.assertEqual(
            "data.granules[0] must contain "
            "['collectionId', 'granuleId', 'files'] properties",
            str(ex.exception),
        )
        mock_task.assert_not_called()

    @patch("extract_filepaths_for_granule.task")
    @patch("extract_filepaths_for_granule.set_optional_event_property")
    def test_handler_raises_error_bad_output(self, _: MagicMock, mock_task: MagicMock):
        """
        Tests that expected error is raised on bad output such as missing granuleId.
        """

        handler_input_event = create_handler_event()
        handler_input_event["config"] = {
            extract_filepaths_for_granule.CONFIG_FILE_BUCKETS_KEY: [
                {
                    "regex": ".*.h5$",
                    "sampleFileName": self.sampleFileName1 + ".h5",
                    "bucket": "protected",
                },
                {
                    "regex": ".*.cmr.xml$",
                    "sampleFileName": self.sampleFileName1 + ".iso.xml",
                    "bucket": "protected",
                },
                {
                    "regex": ".*.h5.mp$",
                    "sampleFileName": self.sampleFileName2 + ".h5.mp",
                    "bucket": "public",
                },
                {
                    "regex": ".*.cmr.json$",
                    "sampleFileName": self.sampleFileName2 + ".cmr.json",
                    "bucket": "public",
                },
            ],
            "buckets": {
                "protected": {"name": self.protected_bucket, "type": "protected"},
                "internal": {"name": self.internal_bucket, "type": "internal"},
                "private": {"name": self.private_bucket, "type": "private"},
                "public": {"name": self.public_bucket, "type": "public"},
            },
        }

        mock_task.return_value = {
            "granules": [{"collectionId": self.collectionId, "keys": ["key1", "key2"]}]
        }
        context = Mock()
        with self.assertRaises(Exception) as ex:
            extract_filepaths_for_granule.handler(handler_input_event, context)
        self.assertEqual(
            str(ex.exception),
            "data.granules[0] must contain "
            "['collectionId', 'granuleId', 'keys'] properties",
        )

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.debug")
    def test_task(self, mock_debug: MagicMock):
        """
        Test successful with four keys returned.
        """
        result = extract_filepaths_for_granule.task(
            self.task_input_event["input"], self.task_input_event["config"]
        )

        exp_key1 = {
            extract_filepaths_for_granule.OUTPUT_KEY_KEY: self.task_input_event[
                "input"
            ]["granules"][0]["files"][0]["key"],
            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.protected_bucket,
        }
        exp_key2 = {
            extract_filepaths_for_granule.OUTPUT_KEY_KEY: self.task_input_event[
                "input"
            ]["granules"][0]["files"][1]["key"],
            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.public_bucket,
        }
        exp_key3 = {
            extract_filepaths_for_granule.OUTPUT_KEY_KEY: self.task_input_event[
                "input"
            ]["granules"][0]["files"][2]["key"],
            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.public_bucket,
        }
        exp_gran = {
            "collectionId": self.task_input_event["input"]["granules"][0][
                "collectionId"
            ],
            "granuleId": self.task_input_event["input"]["granules"][0]["granuleId"],
            "keys": [exp_key1, exp_key2, exp_key3],
        }

        exp_grans = [exp_gran]

        exp_result = {"granules": exp_grans}
        self.assertEqual(exp_result, result)

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.debug")
    def test_task_one_file(self, mock_debug: MagicMock):
        """
        Test with one valid file in input.
        """
        self.task_input_event["input"]["granules"] = [
            {
                "collectionId": self.collectionId,
                "granuleId": self.granuleId,
                "files": [
                    {
                        "key": "MOD09GQ___006/MOD/MOD09GQ.A0219114."
                        "N5aUCG.006.0656338553321.cmr.xml",
                        "bucket": self.input_bucket,
                        "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    }
                ],
            }
        ]
        exp_result = {
            "granules": [
                {
                    "keys": [
                        {
                            extract_filepaths_for_granule.OUTPUT_KEY_KEY: "MOD09GQ___006/MOD/MOD09GQ."  # noqa: E501
                            "A0219114.N5aUCG.006.0656338553321.cmr.xml",
                            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.protected_bucket,  # noqa: E501
                        }
                    ],
                    "collectionId": self.collectionId,
                    "granuleId": self.granuleId,
                }
            ]
        }
        result = extract_filepaths_for_granule.task(
            self.task_input_event["input"], self.task_input_event["config"]
        )
        self.assertEqual(exp_result, result)

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.debug")
    def test_task_no_matching_regex_raises_error(self, mock_debug: MagicMock):
        """
        If no destination bucket can be determined, raise a descriptive error.
        """
        self.task_input_event["input"]["granules"] = [
            {
                "granuleId": self.granuleId,
                "files": [
                    {
                        "key": "MOD09GQ___006/MOD/MOD09GQ.A0219114."
                        "N5aUCG.006.0656338553321.cmr.blah",
                        "bucket": self.input_bucket,
                        "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.blah",
                    }
                ],
            }
        ]
        with self.assertRaises(
            extract_filepaths_for_granule.ExtractFilePathsError
        ) as cm:
            extract_filepaths_for_granule.task(
                self.task_input_event["input"], self.task_input_event["config"]
            )
        self.assertEqual(
            "No matching regex for "
            "'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.blah'",
            str(cm.exception),
        )

    def test_exclude_file_type(self):
        # noinspection SpellCheckingInspection
        """
        Tests the exclude file type filtering. The .cmr filetype will be excluded and
        not show up in the output since the
        "extract_filepaths_for_granule/test/unit_tests/testevents/task_event.json" includes
        "excludedFileExtensions": [".cmr"]
        """
        self.task_input_event["input"]["granules"] = [
            {
                "collectionId": self.collectionId,
                "granuleId": self.granuleId,
                "files": [
                    {
                        "key": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr",
                        "bucket": self.input_bucket,
                        "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr",
                    }
                ],
            }
        ]
        exp_result = {
            "granules": [
                {
                    "keys": [],  # this will be empty since the filetype is .cmr
                    "collectionId": self.collectionId,
                    "granuleId": self.granuleId,
                }
            ]
        }
        result = extract_filepaths_for_granule.task(
            self.task_input_event["input"], self.task_input_event["config"]
        )
        self.assertEqual(exp_result, result)

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.debug")
    def test_task_two_granules(self, mock_debug: MagicMock):
        """
        Test with two granules, one key each.
        """
        collection_id0 = uuid.uuid4().__str__()
        collection_id1 = uuid.uuid4().__str__()

        self.task_input_event["input"]["granules"] = [
            {
                "collectionId": collection_id0,
                "granuleId": self.granuleId,
                "files": [
                    {
                        "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        "key": "MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        "bucket": self.input_bucket,
                    }
                ],
            },
            {
                "collectionId": collection_id1,
                "granuleId": self.granuleId,
                "files": [
                    {
                        "fileName": "MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                        "key": "MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                        "bucket": self.input_bucket,
                    }
                ],
            },
        ]

        exp_result = {
            "granules": [
                {
                    "keys": [
                        {
                            extract_filepaths_for_granule.OUTPUT_KEY_KEY: "MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",  # noqa: E501
                            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.protected_bucket,  # noqa: E501
                        }
                    ],
                    "collectionId": collection_id0,
                    "granuleId": self.granuleId,
                },
                {
                    "keys": [
                        {
                            extract_filepaths_for_granule.OUTPUT_KEY_KEY: "MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",  # noqa: E501
                            extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY: self.protected_bucket,  # noqa: E501
                        }
                    ],
                    "collectionId": collection_id1,
                    "granuleId": self.granuleId,
                },
            ]
        }

        result = extract_filepaths_for_granule.task(
            self.task_input_event["input"], self.task_input_event["config"]
        )
        self.assertEqual(exp_result, result)

        # Validate the output is correct by matching with the output schema
        _OUTPUT_VALIDATE(exp_result)

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.debug")
    def test_task_use_recovery_override_bucket(self, mock_debug: MagicMock):
        """
        Test no 'granules' key in input event.
        """
        self.task_input_event["input"]["granules"][0][
            extract_filepaths_for_granule.INPUT_GRANULE_RECOVERY_BUCKET_OVERRIDE_KEY
        ] = uuid.uuid4().__str__()

        result = extract_filepaths_for_granule.task(
            self.task_input_event["input"], self.task_input_event["config"]
        )
        self.assertEqual(
            self.task_input_event["input"]["granules"][0][
                extract_filepaths_for_granule.INPUT_GRANULE_RECOVERY_BUCKET_OVERRIDE_KEY
            ],
            result["granules"][0]["keys"][0][
                extract_filepaths_for_granule.OUTPUT_DESTINATION_BUCKET_KEY
            ],
        )

    def test_exclude_file_types(self):
        """
        Testing filtering of exclude file types.
        """
        result_true = extract_filepaths_for_granule.should_exclude_files_type(
            "s3://test-bucket/exclude.xml", [".xml"]
        )
        result_false = extract_filepaths_for_granule.should_exclude_files_type(
            "s3://test-bucket/will_not_exclude.cmr", [".xml", ".met"]
        )
        self.assertEqual(True, result_true)
        self.assertEqual(False, result_false)

    # noinspection PyUnusedLocal
    @patch("extract_filepaths_for_granule.LOGGER.info")
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
        extract_filepaths_for_granule.set_optional_event_property(
            mock_event, mock_target_path_cursor, []
        )

        # set asyncOperationId to non-null value
        self.assertEqual(None, mock_event["config0"][key0])
        self.assertEqual(key1_value, mock_event["config0"][key1])
        self.assertEqual(key2_value, mock_event["config1"][key2])


if __name__ == "__main__":
    unittest.main(argv=["start"])
