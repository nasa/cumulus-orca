"""
Name: test_extract_filepaths_for_granule.py

Description:  Unit tests for extract_file_paths_for_granule.py.
"""
import unittest
from unittest.mock import Mock
from cumulus_logger import CumulusLogger
from helpers import LambdaContextMock, create_handler_event, create_task_event
import extract_filepaths_for_granule


class TestExtractFilePaths(unittest.TestCase):
    """
    TestExtractFilePaths.
    """

    def setUp(self):
        self.context = LambdaContextMock()
        self.mock_error = CumulusLogger.error
        self.task_input_event = create_task_event()

    def tearDown(self):
        CumulusLogger.error = self.mock_error

    def test_handler(self):
        """
        Test successful with four keys returned.
        todo: That is not what this test does.
        """
        handler_input_event = create_handler_event()
        exp_msg = "KeyError: \"event['config']['protected-bucket']\" is required"
        try:
            extract_filepaths_for_granule.handler(handler_input_event, self.context)
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_msg, str(ex))

    def test_task(self):
        """
        Test successful with four keys returned.
        """
        result = extract_filepaths_for_granule.task(self.task_input_event, self.context)

        exp_key1 = {'key': self.task_input_event['input']['granules'][0]['files'][0]['key'],
                    'dest_bucket': 'sndbx-cumulus-protected'}
        exp_key2 = {'key': self.task_input_event['input']['granules'][0]['files'][1]['key'],
                    'dest_bucket': 'sndbx-cumulus-public'}
        exp_key3 = {'key': self.task_input_event['input']['granules'][0]['files'][2]['key'],
                    'dest_bucket': None}
        exp_key4 = {'key': self.task_input_event['input']['granules'][0]['files'][3]['key'],
                    'dest_bucket': 'sndbx-cumulus-public'}
        exp_gran = {
            'dataType': 'MOD09GQ_test-jk2-IngestGranuleSuccess-1558420117156',
            'files': [{'bucket': 'cumulus-test-sandbox-protected',
                       'duplicate_found': 'True',
                       'fileName': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5',
                       'key': 'MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5',
                       'path': 'jk2-IngestGranuleSuccess-1558420117156-test-data/files',
                       'size': 1098034,
                       'type': 'data',
                       'url_path': '{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{extractYear(cmrMetadata.Granule.Temporal.RangeDateTime.BeginningDateTime)}/{substring(file.name, '
                                   '0, 3)}'},
                      {'bucket': 'cumulus-test-sandbox-private',
                       'duplicate_found': 'True',
                       'fileName': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.mp',
                       'key': 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.mp',
                       'path': 'jk2-IngestGranuleSuccess-1558420117156-test-data/files',
                       'size': 21708,
                       'type': 'metadata',
                       'url_path': '{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, '
                                   '0, 3)}'},
                      {'bucket': 'cumulus-test-sandbox-public',
                       'duplicate_found': 'True',
                       'fileName': 's3://cumulus-test-sandbox-public/MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg',
                       'key': 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg',
                       'path': 'jk2-IngestGranuleSuccess-1558420117156-test-data/files',
                       'size': 9728,
                       'type': 'browse',
                       'url_path': '{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, '
                                   '0, 3)}'},
                      {'bucket': 'cumulus-test-sandbox-protected-2',
                       'fileName': 's3://cumulus-test-sandbox-protected-2/MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.json',
                       'key': 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.json',
                       'name': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.json',
                       'type': 'metadata',
                       'url_path': '{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, '
                                   '0, 3)}'}],
            'granuleId': self.task_input_event['input']['granules'][0]['granuleId'],
            'keys': [exp_key1, exp_key2, exp_key3, exp_key4],
            'version': '006'
        }

        exp_grans = [exp_gran]

        exp_result = {
            'granules': exp_grans
        }
        self.assertEqual(exp_result, result)

    def test_task_no_granules(self):
        """
        Test no 'granules' key in input event.
        """
        self.task_input_event['input'].pop('granules', None)
        exp_err = "KeyError: \"event['input']['granules']\" is required"
        CumulusLogger.error = Mock()
        try:
            extract_filepaths_for_granule.task(self.task_input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_task_no_granule(self):
        """
        Test no granuleId in input event.
        """
        self.task_input_event['input']['granules'][0] = {"files": []}

        exp_err = "KeyError: \"event['input']['granules'][]['granuleId']\" is required"
        CumulusLogger.error = Mock()
        try:
            extract_filepaths_for_granule.task(self.task_input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_task_no_files(self):
        """
        Test no files in input event.
        """
        self.task_input_event['input']['granules'][0].pop('files', None)
        self.task_input_event['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321"}]

        exp_err = "KeyError: \"event['input']['granules'][]['files']\" is required"
        try:
            extract_filepaths_for_granule.task(self.task_input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_task_no_filepath(self):
        """
        Test no key in input event.
        """
        self.task_input_event['input'].pop('granules', None)
        self.task_input_event['config']['protected-bucket'] = "my_protected_bucket"
        self.task_input_event['config']['internal-bucket'] = "my_internal_bucket"
        self.task_input_event['config']['private-bucket'] = "my_private_bucket"
        self.task_input_event['config']['public-bucket'] = "my_public_bucket"
        self.task_input_event['config']['file-buckets'] = (
            [{'regex': '.*.h5$', 'sampleFileName': 'L_10-420.h5', 'bucket': 'protected'},
             {'regex': '.*.iso.xml$', 'sampleFileName': 'L_10-420.iso.xml', 'bucket': 'protected'},
             {'regex': '.*.h5.mp$', 'sampleFileName': 'L_10-420.h5.mp', 'bucket': 'public'},
             {'regex': '.*.cmr.json$', 'sampleFileName': 'L_10-420.cmr.json', 'bucket': 'public'}])
        self.task_input_event['input']['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2"
                }]}]
        exp_err = "KeyError: \"event['input']['granules'][]['files']['key']\" is required"
        try:
            extract_filepaths_for_granule.task(self.task_input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_task_one_file(self):
        """
        Test with one valid file in input.
        """
        self.task_input_event['input']['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "key":
                        "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2",
                    "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"
                }]}]
        exp_result = {
            'granules': [
                {
                    'files': [
                        {
                            'bucket': "cumulus-test-sandbox-protected-2",
                            'fileName': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml',
                            'key': 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'
                        }
                    ],
                    'keys': [{'key': 'MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml',
                              'dest_bucket': 'sndbx-cumulus-protected'}],
                    'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'}]}
        result = extract_filepaths_for_granule.task(self.task_input_event, self.context)
        self.assertEqual(exp_result, result)

    def test_task_two_granules(self):
        """
        Test with two granules, one key each.
        """

        self.task_input_event['input']['granules'] = \
            [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
              "files": [
                  {
                      "fileName": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "key": "MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "bucket": "cumulus-test-sandbox-protected-2"
                  }
              ]
              },
             {
                 "granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321",
                 "files": [
                     {
                         "fileName": "MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "key": "MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "bucket": "cumulus-test-sandbox-protected-2"
                     }
                 ]
             }
             ]
        exp_result = {'granules': [
            {'keys': [{'key': 'MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml',
                       'dest_bucket': 'sndbx-cumulus-protected'}],
             'files': [
                 {
                     'bucket': 'cumulus-test-sandbox-protected-2',
                     'fileName': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml',
                     'key': 'MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'
                 }
             ],
             'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'},
            {'keys': [{'key': 'MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml',
                       'dest_bucket': 'sndbx-cumulus-protected'}],
             'files': [
                 {
                     'bucket': 'cumulus-test-sandbox-protected-2',
                     'fileName': 'MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml',
                     'key': 'MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml'
                 }
             ],
             'granuleId': 'MOD09GQ.A0219115.N5aUCG.006.0656338553321'}]}

        result = extract_filepaths_for_granule.task(self.task_input_event, self.context)
        self.assertEqual(exp_result, result)


if __name__ == '__main__':
    unittest.main(argv=['start'])
