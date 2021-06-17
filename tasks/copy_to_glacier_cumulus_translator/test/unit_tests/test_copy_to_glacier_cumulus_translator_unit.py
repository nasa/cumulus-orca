"""
Name: test_copy_to_glacier_cumulus_translator_unit.py

Description:  Unit tests for copy_to_glacier_cumulus_translator.py.
"""
import unittest
import uuid
from unittest.mock import MagicMock, patch, Mock

import jsonschema

import copy_to_glacier_cumulus_translator


class TestCopyToGlacierCumulusTranslatorUnit(
    unittest.TestCase
):  # pylint: disable-msg=too-many-instance-attributes
    """
    TestCopyToGlacierCumulusTranslator.
    """

    # noinspection PyPep8Naming
    @patch("run_cumulus_task.run_cumulus_task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_happy_path(
            self,
            mock_setMetadata: MagicMock,
            mock_run_cumulus_task: MagicMock
    ):
        """
        Basic path with all information present.
        """
        event = Mock()
        context = Mock()
        result = copy_to_glacier_cumulus_translator.handler(event, context)

        mock_setMetadata.assert_called_once_with(event, context)
        mock_run_cumulus_task.assert_called_once_with(
            copy_to_glacier_cumulus_translator.task, event, context
        )
        self.assertEqual(mock_run_cumulus_task.return_value, result)

    @patch("copy_to_glacier_cumulus_translator.task")
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_passthrough(self,
                                 mock_setMetadata: MagicMock,
                                 mock_task: MagicMock):
        expected_config = {
            "file_mapping": {
                "name": "nameKey",
                "filepath": "pathKey",
                "bucket": "bucketKey",
                "filename": "filenameKey"
            }
        }
        expected_input = {"granules": [
            {
                "granuleId": "some_granule_id",
                "files": []
            }
        ]}
        event = {
            "task_config": expected_config,
            "payload": expected_input
        }

        context = Mock()

        mock_task.return_value = {"granules": [{"granuleId": "some_granule_id", "files": []}]}

        result = copy_to_glacier_cumulus_translator.handler(event, context)
        self.assertEqual(mock_task.return_value, result['payload'])
        mock_task.assert_called_once_with({"input": expected_input, "config": expected_config}, context)

    # noinspection PyPep8Naming
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_and_task_back_and_forth(self,
                                             mock_setMetadata: MagicMock):
        """
        Tests a happy-path with task to make sure CMA doesn't raise issues.
        """
        expected_config = {
            "file_mapping": {
                "name": "nameKey",
                "filepath": "pathKey",
                "bucket": "bucketKey",
                "filename": "filenameKey"
            }
        }
        expected_input = {"granules": [
            {
                "granuleId": "some_granule_id",
                "files": [{
                    "nameKey": "someName",
                    "pathKey": "somePath",
                    "bucketKey": "someBucket",
                    "filenameKey": "someFilename"
                }]
            }
        ]}
        event = {
            "task_config": expected_config,
            "payload": expected_input
        }
        context = Mock()

        result = copy_to_glacier_cumulus_translator.handler(event, context)
        self.assertEqual({'granules': [{'files': [{'bucket': 'someBucket',
                                                   'filename': 'someFilename',
                                                   'filepath': 'somePath',
                                                   'name': 'someName'}],
                                        'granuleId': 'some_granule_id'}]}, result['payload'])

    # noinspection PyPep8Naming
    @patch("cumulus_logger.CumulusLogger.setMetadata")
    def test_handler_rejects_bad_input(self,
                                       mock_setMetadata: MagicMock):
        expected_config = {
            "file_mapping": {
                "name": "nameKey",
                "filepath": "pathKey",
                "bucket": "bucketKey",
                "filename": "filenameKey"
            }
        }
        expected_input = {"granules": [
            {
                "granule_id": "some_granule_id",  # this is the wrong format. Should be "granuleId"
                "files": [{
                    "nameKey": "someName",
                    "pathKey": "somePath",
                    "bucketKey": "someBucket",
                    "filenameKey": "someFilename"
                }]
            }
        ]}
        event = {
            "task_config": expected_config,
            "payload": expected_input
        }
        context = Mock()

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            copy_to_glacier_cumulus_translator.handler(event, context)

    def test_task_happy_path(self):
        granule_id = uuid.uuid4().__str__()

        file0_name = uuid.uuid4().__str__() + ".jpg"
        file0_path = uuid.uuid4().__str__() + '/' + file0_name
        file0_bucket = uuid.uuid4().__str__()
        file0_source = "s3://" + file0_path

        file1_name = uuid.uuid4().__str__() + ".jpg"
        file1_path = uuid.uuid4().__str__() + '/' + file1_name
        file1_bucket = uuid.uuid4().__str__()
        file1_source = "s3://" + file1_path

        expected_config = {
            "file_mapping": {
                "name": "nameKey",
                "filepath": "pathKey",
                "bucket": "bucketKey",
                "filename": "filenameKey"
            }
        }
        expected_input = {"granules": [
            {
                "granuleId": granule_id,
                "files": [
                    {
                        "nameKey": file0_name,
                        "pathKey": file0_path,
                        "bucketKey": file0_bucket,
                        "filenameKey": file0_source
                    },
                    {
                        "nameKey": file1_name,
                        "pathKey": file1_path,
                        "bucketKey": file1_bucket,
                        "filenameKey": file1_source
                    }
                ]
            }
        ]}
        event = {
            "config": expected_config,
            "input": expected_input
        }
        context = Mock()

        result = copy_to_glacier_cumulus_translator.task(event, context)
        self.assertEqual({'granules': [{'files': [
            {'bucket': file0_bucket,
             'filename': file0_source,
             'filepath': file0_path,
             'name': file0_name},
            {'bucket': file1_bucket,
             'filename': file1_source,
             'filepath': file1_path,
             'name': file1_name}
        ],
            'granuleId': granule_id}]}, result)

    def test_task_missing_filename_key(self):
        """
        If no translation key for filename is given, infer from bucket and filepath.
        """
        granule0_id = uuid.uuid4().__str__()
        granule1_id = uuid.uuid4().__str__()

        file0_name = uuid.uuid4().__str__() + ".jpg"
        file0_path = uuid.uuid4().__str__() + '/' + file0_name
        file0_bucket = uuid.uuid4().__str__()
        file0_source = "s3://" + file0_bucket + '/' + file0_path

        file1_name = uuid.uuid4().__str__() + ".jpg"
        file1_path = uuid.uuid4().__str__() + '/' + file1_name
        file1_bucket = uuid.uuid4().__str__()
        file1_source = "s3://" + file1_bucket + '/' + file1_path

        expected_config = {
            "file_mapping": {
                "name": "nameKey",
                "filepath": "pathKey",
                "bucket": "bucketKey"
            }
        }
        expected_input = {"granules": [
            {
                "granuleId": granule0_id,
                "files": [
                    {
                        "nameKey": file0_name,
                        "pathKey": file0_path,
                        "bucketKey": file0_bucket
                    }
                ]
            },
            {
                "granuleId": granule1_id,
                "files": [
                    {
                        "nameKey": file1_name,
                        "pathKey": file1_path,
                        "bucketKey": file1_bucket
                    }
                ]
            }
        ]}
        event = {
            "config": expected_config,
            "input": expected_input
        }
        context = Mock()

        result = copy_to_glacier_cumulus_translator.task(event, context)
        self.assertEqual({'granules':
            [
                {
                    'granuleId': granule0_id,
                    'files': [
                        {'bucket': file0_bucket,
                         'filename': file0_source,
                         'filepath': file0_path,
                         'name': file0_name}
                    ]
                },
                {
                    'granuleId': granule1_id,
                    'files': [
                        {'bucket': file1_bucket,
                         'filename': file1_source,
                         'filepath': file1_path,
                         'name': file1_name}
                    ]
                }
            ]}, result)
