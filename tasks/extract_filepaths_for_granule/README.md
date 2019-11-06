**Lambda function extract_filepaths_for_granule **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
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

Name                               Stmts   Miss  Cover
------------------------------------------------------
extract_filepaths_for_granule.py      50      1    98%
----------------------------------------------------------------------
Ran 8 tests in 0.781s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\extract_filepaths_for_granule
(podr) λ pylint extract_filepaths_for_granule.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_extract_file_paths_for_granule.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

pylint test/helpers.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
    cd tasks\extract_filepaths_for_granule
    rm -rf build
    rm -rf venv
    mkdir build
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -t build -r requirements.txt
    deactivate
    cp *.py build/
    cd build
    zip -r ../task.zip .
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  The easiest way to test is to use the DrRecoveryWorkflowStateMachine.
    You can use the test event in tasks/extract_filepaths_for_granule/test/testevents/StepFunction.json.
    Edit the ['payload']['granules']['keys'] values as needed to be the file(s) you wish to restore.
    Edit the ['cumulus_meta']['execution_name'] to be something unique (like yyyymmdd_hhmm). Then
    copy and paste the same value to the execution name field above the input field.
    
2.  Execute the workflow. Once it passes the extract step, you can look at the output from it.
```
<a name="pydoc"></a>
## pydoc extract_filepaths_for_granule
```
NAME
    extract_filepaths_for_granule - Name: extract_filepaths_for_granule.py

DESCRIPTION
    Description:  Extracts the keys (filepaths) for a granule's files from a Cumulus Message.

CLASSES
    builtins.Exception(builtins.BaseException)
        ExtractFilePathsError

    class ExtractFilePathsError(builtins.Exception)
     |  Exception to be raised if any errors occur
     
FUNCTIONS
    handler(event, context)
        Lambda handler. Extracts the key's for a granule from an input dict.

        Args:
            event (dict): A dict with the following keys:

                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of a granule.
                    files (list(dict)): list of dict with the following keys:
                        key (string): The key of the file to be returned.
                        other dictionary keys may be included, but are not used.
                    other dictionary keys may be included, but are not used.

                Example: event: {'granules': [
                                      {'granuleId': 'granxyz',
                                       'version": '006',
                                       'files': [
                                            {'name': 'file1',
                                             'key': 'key1',
                                             'filename': 's3://dr-test-sandbox-protected/file1',
                                             'type': 'metadata'} ]
                                       }
                                    ]
                                 }

            context (Object): None

        Returns:
            dict: A dict with the following keys:

                'granules' (list(dict)): list of dict with the following keys:
                    'granuleId' (string): The id of a granule.
                    'keys' (list(string)): list of keys for the granule.

            Example:
                {"granules": [{"granuleId": "granxyz",
                             "keys": ["key1",
                                           "key2"]}]}

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
```
