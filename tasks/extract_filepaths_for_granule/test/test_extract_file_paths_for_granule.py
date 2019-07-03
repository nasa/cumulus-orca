"""
Name: test_extract_filepaths_for_granule.py

Description:  Unit tests for extract_file_paths_for_granule.py.
"""
import unittest
from helpers import LambdaContextMock, create_event
import extract_filepaths_for_granule

class TestExtractFilePaths(unittest.TestCase):
    """
    TestExtractFilePaths.
    """
    def setUp(self):
        self.context = LambdaContextMock()
        self.input_event = create_event()

    def tearDown(self):
        pass

    def test_handler(self):
        """
        Test successful with four filepaths returned.
        """
        result = extract_filepaths_for_granule.handler(self.input_event, self.context)
        exp_result = {}
        exp_grans = []
        exp_gran = {}
        exp_files = []
        exp_gran['granuleId'] = self.input_event['payload']['granules'][0]['granuleId']
        exp_files.append(self.input_event['payload']['granules'][0]['files'][0]['key'])
        exp_files.append(self.input_event['payload']['granules'][0]['files'][1]['key'])
        exp_files.append(self.input_event['payload']['granules'][0]['files'][2]['key'])
        exp_files.append(self.input_event['payload']['granules'][0]['files'][3]['key'])
        exp_gran['filepaths'] = exp_files
        exp_grans.append(exp_gran)

        exp_result['granules'] = exp_grans
        self.assertEqual(exp_result, result['payload'])

    def test_handler_no_granules(self):
        """
        Test no 'granules' key in input event.
        """
        self.input_event['payload'].pop('granules', None)
        exp_err = "KeyError: \"event['input']['granules']\" is required"
        try:
            extract_filepaths_for_granule.handler(self.input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_granule(self):
        """
        Test no granuleId in input event.
        """
        self.input_event['payload']['granules'][0] = {"files": []}

        exp_err = "KeyError: \"event['input']['granules'][]['granuleId']\" is required"
        try:
            extract_filepaths_for_granule.handler(self.input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_files(self):
        """
        Test no files in input event.
        """
        self.input_event['payload']['granules'][0].pop('files', None)
        self.input_event['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321"}]

        exp_err = "KeyError: \"event['input']['granules'][]['files']\" is required"
        try:
            extract_filepaths_for_granule.handler(self.input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_no_filepath(self):
        """
        Test no filepath in input event.
        """
        self.input_event['payload'].pop('granules', None)
        self.input_event['payload']['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2"
                }]}]
        exp_err = "KeyError: \"event['input']['granules'][]['files']['key']\" is required"
        try:
            extract_filepaths_for_granule.handler(self.input_event, self.context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(exp_err, str(ex))

    def test_handler_one_file(self):
        """
        Test with one valid file in input.
        """
        self.input_event['payload']['granules'] = [{
            "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "files": [
                {
                    "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "key":
                        "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                    "bucket": "cumulus-test-sandbox-protected-2"
                }]}]
        exp_result = {'granules': [
            {'filepaths': ['MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'],
             'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'}]}
        result = extract_filepaths_for_granule.handler(self.input_event, self.context)
        self.assertEqual(exp_result, result['payload'])

    def test_handler_two_granules(self):
        """
        Test with two granules, one filepath each.
        """

        self.input_event['payload']['granules'] = \
            [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
              "files": [
                  {
                      "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "key": "MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                      "bucket": "cumulus-test-sandbox-protected-2"
                  }
              ]
              },
             {
                 "granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321",
                 "files": [
                     {
                         "name": "MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "key": "MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml",
                         "bucket": "cumulus-test-sandbox-protected-2"
                     }
                 ]
             }
             ]
        exp_result = {'granules': [
            {'filepaths': ['MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml'],
             'granuleId': 'MOD09GQ.A0219114.N5aUCG.006.0656338553321'},
            {'filepaths': ['MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml'],
             'granuleId': 'MOD09GQ.A0219115.N5aUCG.006.0656338553321'}]}

        result = extract_filepaths_for_granule.handler(self.input_event, self.context)
        self.assertEqual(exp_result, result['payload'])



if __name__ == '__main__':
    unittest.main(argv=['start'])
