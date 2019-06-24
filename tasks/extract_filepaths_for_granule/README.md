**Lambda function extract_filepaths_for_granule **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
- [pydoc extract_filepaths_for_granule](#pydoc)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
Run the unit tests with code coverage:

λ activate podr

(podr) λ cd C:\devpy\poswotdr\tasks\extract_filepaths_for_granule
(podr) λ nosetests --with-coverage --cover-erase --cover-package=extract_filepaths_for_granule -v
test_handler (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_no_filepath (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_no_files (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_no_glacier_bucket (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_no_granule (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_no_granules (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_one_file (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok
test_handler_two_granules (test_extract_file_paths_for_granule.TestExtractFilePaths) ... ok

Name                               Stmts   Miss  Cover
------------------------------------------------------
extract_filepaths_for_granule.py      26      0   100%
----------------------------------------------------------------------
Ran 8 tests in 0.045s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\extract_filepaths_for_granule
(podr) λ pylint extract_filepaths_for_granule.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
    cd tasks\extract_filepaths_for_granule
    zip task.zip *.py
```
<a name="pydoc"></a>
## pydoc extract_filepaths_for_granule
```
NAME
    extract_filepaths_for_granule - Name: extract_filepaths_for_granule.py

DESCRIPTION
    Description:  Lambda handler that extracts the filepath's for a granule from an input dict.

CLASSES
    builtins.Exception(builtins.BaseException)
        ExtractFilePathsError

    class ExtractFilePathsError(builtins.Exception)
     |  Exception to be raised if any errors occur
     
FUNCTIONS
    handler(event, context)
        Lambda handler. Extracts the filepath's for a granule from an input dict.

        Args:
            event (dict): A dict with the following keys:

                glacierBucket (string) :  The name of a glacier bucket.
                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of a granule.
                    files (list(dict)): list of dict with the following keys:
                        filepath (string): The key (filepath) of the file.
                        other keys may be included, but are not used.
                    other keys may be included, but are not used.

                Example: event: {'glacierBucket': 'some_bucket',
                                 'granules': [
                                      {'granuleId': 'granxyz',
                                       'version": '006',
                                       'files': [
                                            {'name': 'file1',
                                             'filepath': 'filepath1',
                                             'filename': 's3://dr-test-sandbox-protected/file1',
                                             'type': 'metadata'} ]
                                       }
                                    ]
                                 }

            context (Object): None

        Returns:
            dict: A dict with the following keys:

                'glacierBucket' (string): The name of a glacier bucket.
                'granules' (list(dict)): list of dict with the following keys:
                    'granuleId' (string): The id of a granule.
                    'filepaths' (list(string)): list of filepaths for the granule.

            Example:
                {"glacierBucket": "some_bucket",
                 "granules": [{"granuleId": "granxyz",
                             "filepaths": ["filepath1",
                                           "filepath2"]}]}

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
```