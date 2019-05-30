import unittest
import json
import extract_filepaths_for_granule

class TestExtractFilePaths(unittest.TestCase):

    def setUp(self):
        self.exp_event = {
  "glacierBucket": "some_bucket",
  "granules":
    [{
      "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
      "dataType": "MOD09GQ_test-jk2-IngestGranuleSuccess-1558420117156",
      "version": "006",
      "files": [
        {
          "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
          "filepath": "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
          "bucket": "cumulus-test-sandbox-protected",
          "filename": "s3://cumulus-test-sandbox-protected/MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf",
          "path": "jk2-IngestGranuleSuccess-1558420117156-test-data/files",
          "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{extractYear(cmrMetadata.Granule.Temporal.RangeDateTime.BeginningDateTime)}/{substring(file.name, 0, 3)}",
          "type": "data",
          "duplicate_found": True,
          "size": 1098034
        },
        {
          "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met",
          "filepath": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met",
          "bucket": "cumulus-test-sandbox-private",
          "filename": "s3://cumulus-test-sandbox-private/MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.hdf.met",
          "path": "jk2-IngestGranuleSuccess-1558420117156-test-data/files",
          "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, 0, 3)}",
          "type": "metadata",
          "duplicate_found": True,
          "size": 21708
        },
        {
          "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg",
          "filepath": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg",
          "bucket": "cumulus-test-sandbox-public",
          "filename": "s3://cumulus-test-sandbox-public/MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321_ndvi.jpg",
          "path": "jk2-IngestGranuleSuccess-1558420117156-test-data/files",
          "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, 0, 3)}",
          "type": "browse",
          "duplicate_found": True,
          "size": 9728
        },
        {
          "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
          "filepath": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
          "bucket": "cumulus-test-sandbox-protected-2",
          "filename": "s3://cumulus-test-sandbox-protected-2/MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
          "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, 0, 3)}",
          "type": "metadata"
        }
      ]
    }
  ]
}
        self.exp_context = None

    def test_handler(self):
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
        expected_result = json.dumps(exp_result)
        print("expected_result: ", expected_result)
        self.assertEqual(expected_result, result)

    def test_handler_no_glacier_bucket(self):
        self.exp_event.pop('glacierBucket',None)
        expErr = "KeyError: 'event.glacierBucket' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(expErr,str(ex))

    def test_handler_no_granules(self):
        self.exp_event.pop('granules', None)
        expErr = "KeyError: 'event.granules' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(expErr,str(ex))

    def test_handler_no_granule(self):
        self.exp_event['granules'][0] =  {
 #              "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                "files": []
            }

        expErr = "KeyError: 'event.granules[{granuleId' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(expErr,str(ex))

    def test_handler_no_files(self):
        self.exp_event.pop('granules', None)
        self.exp_event['granules']  = [{
                "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                #"files": [
            }
        ]

        expErr = "KeyError: 'event.granules[{files' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(expErr, str(ex))

    def test_handler_no_filepath(self):
        self.exp_event.pop('granules', None)
        self.exp_event['granules'] = [{
                "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                "files": [
                    {
                        "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        #"filepath": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        "bucket": "cumulus-test-sandbox-protected-2"
                    }
                ]
            }
         ]
        expErr = "KeyError: 'event.granules[{files[{filepath' is required"
        try:
            extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
            self.fail("ExtractFilePathsError expected")
        except extract_filepaths_for_granule.ExtractFilePathsError as ex:
            self.assertEqual(expErr, str(ex))

    def test_handler_one_file(self):
        self.exp_event['granules'] = [ {
                "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
                "files": [
                    {
                        "name": "MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        "filepath": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml",
                        "bucket": "cumulus-test-sandbox-protected-2"
                    }
                ]
            }
         ]
        expResult = '{"glacierBucket": "some_bucket", "granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321", "filepaths": ["MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"]}]}'
        result = extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
        self.assertEqual(expResult, result)

    def test_handler_two_granules(self):
        self.exp_event['granules'] = [ {
                "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
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
        expResult = '{"glacierBucket": "some_bucket", ' \
                    '"granules": [{"granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321", ' \
                    '"filepaths": ["MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.cmr.xml"]}, ' \
                    '{"granuleId": "MOD09GQ.A0219115.N5aUCG.006.0656338553321", ' \
                    '"filepaths": ["MOD/MOD09GQ.A0219115.N5aUCG.006.0656338553321.cmr.xml"]}]}'
        result = extract_filepaths_for_granule.handler(self.exp_event, self.exp_context)
        self.assertEqual(expResult, result)

    def tearDown(self):

        pass

if __name__ == '__main__':
    unittest.main(argv=['start'])
