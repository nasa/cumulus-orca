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

    def test_1_exclude_file_types_excluded(self):
        """
        Testing exclude file types to be excluded
        """
        excluded_flag = should_exclude_files_type(self.excluded_file, ['.example'])
        self.assertEqual(excluded_flag, True)

    def test_2_excluded_file_types_not_excluded(self):
        """
        Testing exclude file types not to be excluded
        """

        not_excluded_flag = should_exclude_files_type(self.not_excluded_file, ['.example'])
        self.assertEqual(not_excluded_flag, False)

    def test_3_get_source_bucket_and_key(self):
        """
        Testing get source bucket and key
        """
        no_prefix_source = get_source_bucket_and_key(self.excluded_file)
        self.assertEqual(no_prefix_source[1], 'test-bucket')
        self.assertEqual(no_prefix_source[2], 'this_file_should_be_exclude.example')

        one_prefix_source = get_source_bucket_and_key(self.not_excluded_file)
        self.assertEqual(one_prefix_source[1], 'test-bucket')
        self.assertEqual(one_prefix_source[2], 'prefix/this_file_should_not_be_exclude.txt')

        two_prefix_source = get_source_bucket_and_key(self.two_prefix_file)
        self.assertEqual(two_prefix_source[1], 'test-bucket')
        self.assertEqual(two_prefix_source[2], 'prefix1/prefix2/file.txt')

    def test_4_get_bucket(self):
        """
        Testing get bucket
        """
        with open(self.event_path) as f:
            event = json.load(f)
            filename = path.basename(event.get('input', [])[0])
            files = event.get('config').get('collection').get('files', [])
            bucket = get_bucket_name_for_filename(filename, files)
            self.assertEqual(bucket, 'protected')

    def test_task_happy_path(self):
        """
        Basic path with buckets present.
        """
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        filename = 'test' + uuid.uuid4().__str__() + '.ext'
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        source_key = f'file-staging/blah/{collection_name}__{collection_version}/{filename}'
        granule_url = f"s3://{source_bucket_name}/{source_key}"

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(side_effect=[None])
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': [granule_url],
            'config': {
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                    'files': [
                        {
                            'regex': '[a]+',
                            'bucket': 'bad_bucket'
                        },
                        {
                            'regex': '^test*.',
                            'bucket': source_bucket_name
                        }
                    ],
                    COLLECTION_URL_PATH_KEY: collection_url_path
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

        self.assertEqual(event['input'], result['input'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        granules = list(granules)
        self.assertEqual(1, len(granules))
        granule = granules[0]
        self.assertEqual(filename, granule['granuleId'])
        self.assertEqual(1, len(granule['files']))
        file = granule['files'][0]
        self.assertEqual(f"{collection_name}__{collection_version}", file['path'])
        self.assertEqual(f"{collection_name}__{collection_version}", file['url_path'])
        self.assertEqual(source_bucket_name, file['bucket'])
        self.assertEqual(granule_url, file['filename'])
        self.assertEqual(granule_url, file['name'])

        s3_cli.head_object.assert_called_once_with(Bucket=source_bucket_name, Key=source_key)
        s3_cli.copy.assert_has_calls([call(
            {'Bucket': source_bucket_name, 'Key': source_key},
            destination_bucket_name,
            f"{collection_url_path}/{filename}",
            ExtraArgs={
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY',
                'ContentType': content_type
            }
        )])

    def test_task_bucket_not_present(self):
        """
        Bucket not present in collection, should default to 'public' in output.
        Copy still uses passed in bucket name.
        # todo: Why is this the way it is?
        """
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        filename = 'test' + uuid.uuid4().__str__() + '.ext'
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        source_key = f'file-staging/blah/{collection_name}__{collection_version}/{filename}'
        granule_url = f"s3://{source_bucket_name}/{source_key}"

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(side_effect=[None])
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': [granule_url],
            'config': {
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                    'files': [
                        {
                            'regex': '[a]+',
                            'bucket': 'bad_bucket'
                        }
                    ],
                    COLLECTION_URL_PATH_KEY: collection_url_path
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

        self.assertEqual(event['input'], result['input'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        granules = list(granules)
        self.assertEqual(1, len(granules))
        granule = granules[0]
        self.assertEqual(filename, granule['granuleId'])
        self.assertEqual(1, len(granule['files']))
        file = granule['files'][0]
        self.assertEqual(f"{collection_name}__{collection_version}", file['path'])
        self.assertEqual(f"{collection_name}__{collection_version}", file['url_path'])
        self.assertEqual('public', file['bucket'])
        self.assertEqual(granule_url, file['filename'])
        self.assertEqual(granule_url, file['name'])

        s3_cli.head_object.assert_called_once_with(Bucket=source_bucket_name, Key=source_key)
        s3_cli.copy.assert_has_calls([call(
            {'Bucket': source_bucket_name, 'Key': source_key},
            destination_bucket_name,
            f"{collection_url_path}/{filename}",
            ExtraArgs={
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY',
                'ContentType': content_type
            }
        )])

    def test_task_bad_file_type_does_not_halt(self):
        """
        A file whose extension is not safe to copy should NOT be copied between buckets.
        It should also not halt execution, as other files can still be copied.
        """
        bad_file_type = '.garbage'
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        filename = 'test' + uuid.uuid4().__str__() + '.ext'
        bad_filename = 'test' + uuid.uuid4().__str__() + '.' + bad_file_type
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        bad_source_key = f'file-staging/blah/{collection_name}__{collection_version}/{bad_filename}'
        source_key = f'file-staging/blah/{collection_name}__{collection_version}/{filename}'
        bad_granule_url = f"s3://{source_bucket_name}/{bad_source_key}"
        granule_url = f"s3://{source_bucket_name}/{source_key}"

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(side_effect=[None])
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': [bad_granule_url, granule_url],
            'config': {
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                    'files': [
                        {
                            'regex': '[a]+',
                            'bucket': 'bad_bucket'
                        },
                        {
                            'regex': '^test*.',
                            'bucket': source_bucket_name
                        }
                    ],
                    COLLECTION_URL_PATH_KEY: collection_url_path,
                    COLLECTION_META_KEY: {
                        EXCLUDE_FILE_TYPES_KEY: [bad_file_type]
                    }
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

        self.assertEqual(event['input'], result['input'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        granules = list(granules)
        self.assertEqual(2, len(granules), 'There should be a granule even if nothing was copied.')
        granule = granules[1]
        self.assertEqual(filename, granule['granuleId'])
        self.assertEqual(1, len(granule['files']))
        file = granule['files'][0]
        self.assertEqual(f"{collection_name}__{collection_version}", file['path'])
        self.assertEqual(f"{collection_name}__{collection_version}", file['url_path'])
        self.assertEqual(source_bucket_name, file['bucket'])
        self.assertEqual(granule_url, file['filename'])
        self.assertEqual(granule_url, file['name'])

        s3_cli.head_object.assert_called_once_with(Bucket=source_bucket_name, Key=source_key)
        s3_cli.copy.assert_has_calls([call(
            {'Bucket': source_bucket_name, 'Key': source_key},
            destination_bucket_name,
            f"{collection_url_path}/{filename}",
            ExtraArgs={
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY',
                'ContentType': content_type
            }
        )])

    def test_fileStagingDir_overridden(self):
        """
        Overriding fileStagingDir affects output.
        """
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        filename = 'test' + uuid.uuid4().__str__() + '.ext'
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        file_staging_dir = uuid.uuid4().__str__()
        source_key = f'file-staging/blah/{file_staging_dir}/{filename}'
        granule_url = f"s3://{source_bucket_name}/{source_key}"

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(side_effect=[None])
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': [granule_url],
            'config': {
                CONFIG_FILE_STAGING_DIRECTORY_KEY: file_staging_dir,
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                    'files': [
                        {
                            'regex': '[a]+',
                            'bucket': 'bad_bucket'
                        },
                        {
                            'regex': '^test*.',
                            'bucket': source_bucket_name
                        }
                    ],
                    COLLECTION_URL_PATH_KEY: collection_url_path
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

        self.assertEqual(event['input'], result['input'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        granules = list(granules)
        self.assertEqual(1, len(granules))
        granule = granules[0]
        self.assertEqual(filename, granule['granuleId'])
        self.assertEqual(1, len(granule['files']))
        file = granule['files'][0]
        self.assertEqual(file_staging_dir, file['path'])
        self.assertEqual(file_staging_dir, file['url_path'])
        self.assertEqual(source_bucket_name, file['bucket'])
        self.assertEqual(granule_url, file['filename'])
        self.assertEqual(granule_url, file['name'])

        s3_cli.head_object.assert_called_once_with(Bucket=source_bucket_name, Key=source_key)
        s3_cli.copy.assert_has_calls([call(
            {'Bucket': source_bucket_name, 'Key': source_key},
            destination_bucket_name,
            f"{collection_url_path}/{filename}",
            ExtraArgs={
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY',
                'ContentType': content_type
            }
        )])

    def test_url_path_overridden(self):
        """
        Overriding url_path in config affects output.
        """
        collection_name = uuid.uuid4().__str__()
        collection_version = uuid.uuid4().__str__()
        destination_bucket_name = uuid.uuid4().__str__()
        source_bucket_name = uuid.uuid4().__str__()
        filename = 'test' + uuid.uuid4().__str__() + '.ext'
        collection_url_path = uuid.uuid4().__str__()
        content_type = uuid.uuid4().__str__()
        source_key = f'file-staging/blah/{collection_name}__{collection_version}/{filename}'
        granule_url = f"s3://{source_bucket_name}/{source_key}"
        config_url_path = uuid.uuid4().__str__()

        # todo: use 'side_effect' to verify args. It is safer, as current method does not deep-copy args
        boto3.client = Mock()
        s3_cli = boto3.client('s3')
        s3_cli.copy = Mock(side_effect=[None])
        s3_cli.head_object = Mock(return_value={'ContentType': content_type})

        event = {
            'input': [granule_url],
            'config': {
                CONFIG_URL_PATH_KEY: config_url_path,
                CONFIG_COLLECTION_KEY: {
                    COLLECTION_NAME_KEY: collection_name,
                    COLLECTION_VERSION_KEY: collection_version,
                    'files': [
                        {
                            'regex': '[a]+',
                            'bucket': 'bad_bucket'
                        },
                        {
                            'regex': '^test*.',
                            'bucket': source_bucket_name
                        }
                    ],
                    COLLECTION_URL_PATH_KEY: collection_url_path
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

        self.assertEqual(event['input'], result['input'])
        granules = result['granules']
        self.assertIsNotNone(granules)
        granules = list(granules)
        self.assertEqual(1, len(granules))
        granule = granules[0]
        self.assertEqual(filename, granule['granuleId'])
        self.assertEqual(1, len(granule['files']))
        file = granule['files'][0]
        self.assertEqual(f"{collection_name}__{collection_version}", file['path'])
        self.assertEqual(config_url_path, file['url_path'])
        self.assertEqual(source_bucket_name, file['bucket'])
        self.assertEqual(granule_url, file['filename'])
        self.assertEqual(granule_url, file['name'])

        s3_cli.head_object.assert_called_once_with(Bucket=source_bucket_name, Key=source_key)
        s3_cli.copy.assert_has_calls([call(
            {'Bucket': source_bucket_name, 'Key': source_key},
            destination_bucket_name,
            f"{collection_url_path}/{filename}",
            ExtraArgs={
                'StorageClass': 'GLACIER',
                'MetadataDirective': 'COPY',
                'ContentType': content_type
            }
        )])

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
