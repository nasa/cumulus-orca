"""
Name: test_extract_filepaths_for_granule.py

Description:  Unit tests for extract_file_paths_for_granule.py.
"""
import unittest
import json
import extract_filepaths_for_granule

class TestExtractFilePaths(unittest.TestCase):
    """
    TestExtractFilePaths.
    """
    def setUp(self):
        try:
            with open('test/testevents/exp_event.json') as f:
                self.exp_event = json.load(f)
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            with open('testevents/exp_event.json') as f:
                self.exp_event = json.load(f)
        self.exp_context = None

    def tearDown(self):

        pass

    def test_handler(self):
        """
        Test successful with four filepaths returned.
        """
        result = extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)

        exp_result = {}

        exp_result['glacierBucket'] = 'some_bucket'
        exp_grans = []
        exp_gran = {}
        exp_files = []
        exp_gran['granuleId'] = self.exp_event['granules'][0]['granuleId']
        exp_files.append(self.exp_event['granules'][0]['files'][0]['filepath'])
        exp_files.append(self.exp_event['granules'][0]['files'][1]['filepath'])
        exp_files.append(self.exp_event['granules'][0]['files'][2]['filepath'])
        exp_files.append(self.exp_event['granules'][0]['files'][3]['filepath'])
        exp_gran['filepaths'] = exp_files
        exp_grans.append(exp_gran)

        exp_result['granules'] = exp_grans
        self.assertEqual(exp_result, result)

    def test_handler_no_glacier_bucket(self):
        """
        Test no glacier bucket in input event.
        """
        self.exp_event.pop('glacierBucket', None)
        exp_err = "KeyError: 'event.glacierBucket' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_granules(self):
        """
        Test no 'granules' key in input event.
        """
        self.exp_event.pop('granules', None)
        exp_err = "KeyError: 'event.granules' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_granule(self):
        """
        Test no granuleId in input event.
        """
        self.exp_event['granules'][0] = {"files": []}

        exp_err = "KeyError: 'event.granules[{granuleId' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_files(self):
        """
        Test no files in input event.
        """
        self.exp_event.pop('granules', None)
        self.exp_event['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321"}]

        exp_err = "KeyError: 'event.granules[{files' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_filepath(self):
        """
        Test no filepath in input event.
        """
        self.exp_event.pop('granules', None)
        self.exp_event['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2"
                }]}]
        exp_err = "KeyError: 'event.granules[{files[{filepath' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_one_file(self):
        """
        Test with one valid file in input.
        """
        self.exp_event['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "filepath":
                        "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2"
                }]}]
        exp_result = {'glacierBucket': 'some_bucket', 'granules': [
            {'filepaths': ['MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'],
             'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'}]}
        result = extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
        self.assertEqual(exp_result, result)

    def test_handler_two_granules(self):
        """
        Test with two granules, one filepath each.
        """
        self.exp_event['granules'] = \
            [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
              "files": [
                  {
                      "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "filepath": "MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "bucket": "cumulus-test-sandbox-protected-2"
                  }
              ]
              },
             {
                 "granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321",
                 "files": [
                     {
                         "name": "MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "filepath": "MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "bucket": "cumulus-test-sandbox-protected-2"
                     }
                 ]
             }
             ]
        exp_result = {'glacierBucket': 'some_bucket',
                      'granules': [
                          {'filepaths': ['MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'],
                           'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'},
                          {'filepaths': ['MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml'],
                           'granuleId': 'MOD09GQ.A0219115.N5aUCG.006.0656338553321'}]}
        result = extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
        self.assertEqual(exp_result, result)



if __name__ == '__main__':
    unittest.main(argv=['start'])
