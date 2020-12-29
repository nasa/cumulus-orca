import json
import uuid
from os import path
from unittest import TestCase
from unittest.mock import Mock, call

from ..handler import *


class TestCopyToGlacierHandler(TestCase):
    """
    Test copy to glacier handler
    This will test if the function of test copy to glacier work as expected
    """

    excluded_file = 's3://test-bucket/this_file_should_be_exclude.example'
    not_excluded_file = 's3://test-bucket/prefix/this_file_should_not_be_exclude.txt'
    two_prefix_file = 's3://test-bucket/prefix1/prefix2/file.txt'
    path_to_this_file = os.path.abspath(os.path.dirname(__file__))
    event_path = os.path.join(path_to_this_file, "event.json")
    event_granules = {
        'granules': [
            {
                "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
                "dataType": "MOD09GQ",
                "version": "006",
                "files": [
                    {
                        "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318361000,
                        "bucket": "orca-sandbox-protected",
                        "url_path": "MOD09GQ/006/",
                        "type": "",
                        "filename": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
                        "duplicate_found": True
                    },
                    {
                        "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318366000,
                        "bucket": "orca-sandbox-private",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
                        "duplicate_found": True
                    },
                    {
                        "name": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        "path": "MOD09GQ/006",
                        "size": 6,
                        "time": 1608318372000,
                        "bucket": "orca-sandbox-public",
                        "url_path": "MOD09GQ/006",
                        "type": "",
                        "filename": "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
                        "duplicate_found": True
                    },
                    {
                        "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        "bucket": "orca-sandbox-private",
                        "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        "type": "metadata",
                        "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
                        "url_path": "MOD09GQ/006"
                    }
                ]
            }
        ]
    }

    def test_exclude_file_types_excluded(self):
        """
        Testing exclude file types to be excluded
        """
        excluded_flag = should_exclude_files_type(self.excluded_file, ['.example'])
        self.assertEqual(excluded_flag, True)

    def test_excluded_file_types_not_excluded(self):
        """
        Testing exclude file types not to be excluded
        """

        not_excluded_flag = should_exclude_files_type(self.not_excluded_file, ['.example'])
        self.assertEqual(not_excluded_flag, False)

    def test_task_happy_path(self):
        """
        Basic path with buckets present.
        """
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        source_bucket_names = [ file['bucket'] for file in self.event_granules['granules'][0]['files'] ]
        source_keys = [ file['filepath'] for file in self.event_granules['granules'][0]['files'] ]

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(return_value=None)
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': self.event_granules,
            'config': {
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                },
                CONFIG_BUCKETS_KEY: {
                    'bad_bucket': {
                        'name': 'not_glacier'
                    },
                    'glacier': {
                        'name': destination_bucket_name
                    }
                }
            }

        }

        result = task(event, None)

        self.assertEqual(event['input']['granules'], result['granules'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        self.assertEqual(1, len(granules))
        granule = granules[0]
        self.assertEqual(4, len(granule['files']))
        file = granule['files'][0]

        head_object_calls = []
        copy_calls = []
        for i in range(0, len(source_bucket_names)):
            head_object_calls.append(call(Bucket=source_bucket_names[i], Key=source_keys[i]))
            copy_calls.append(call(
                {'Bucket': source_bucket_names[i], 'Key': source_keys[i]},
                destination_bucket_name,
                source_keys[i],
                ExtraArgs={
                    'StorageClass': 'GLACIER',
                    'MetadataDirective': 'COPY',
                    'ContentType': content_type
                }
            ))

        s3_cli.head_object.assert_has_calls(head_object_calls)
        s3_cli.copy.assert_has_calls(copy_calls)

        expected_copied_file_urls = [ file['filename'] for file in self.event_granules['granules'][0]['files'] ]
        self.assertEqual(expected_copied_file_urls, result['copied_to_glacier'])

    def test_task_empty_granules_list(self):
        """
        Basic path with buckets present.
        """
        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock()
        s3_cli.head_object = Mock()

        event = {
            'input': {
                "granules": []
            },
            'config': {
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                },
                CONFIG_BUCKETS_KEY: {
                    'bad_bucket': {
                        'name': 'not_glacier'
                    },
                    'glacier': {
                        'name': destination_bucket_name
                    }
                }
            }

        }

        result = task(event, None)

        self.assertEqual([], result['granules'])
        granules = result['granules']
        self.assertEqual(0, len(granules))

        s3_cli.head_object.assert_not_called()
        s3_cli.copy.assert_not_called()

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
