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
Test successful with four filepaths returned. ... ok
Test no filepath in input event. ... {"message": "KeyError: \"event['input']['granules'][]['files']['key']\" is required", "level": "error", "executions": ["DrRecovery58"], "timestamp": "2019-07-03T09:31:42.365209", "sender": "extract_filepaths_for_granule", "version": 1}
ok
Test no files in input event. ... {"message": "KeyError: \"event['input']['granules'][]['files']\" is required", "level": "error", "executions": ["DrRecovery58"], "timestamp": "2019-07-03T09:31:42.369207", "sender": "extract_filepaths_for_granule", "version": 1}
ok
Test no granuleId in input event. ... {"message": "KeyError: \"event['input']['granules'][]['granuleId']\" is required", "level": "error", "executions": ["DrRecovery58"], "timestamp": "2019-07-03T09:31:42.372210", "sender": "extract_filepaths_for_granule", "version": 1}
ok
Test no 'granules' key in input event. ... {"message": "KeyError: \"event['input']['granules']\" is required", "level": "error", "executions": ["DrRecovery58"], "timestamp": "2019-07-03T09:31:42.375212", "sender": "extract_filepaths_for_granule", "version": 1}
ok
Test with one valid file in input. ... ok
Test with two granules, one filepath each. ... ok

Name                               Stmts   Miss  Cover
------------------------------------------------------
extract_filepaths_for_granule.py      27      0   100%
----------------------------------------------------------------------
Ran 7 tests in 0.792s

```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\extract_filepaths_for_granule
(podr) λ pylint extract_filepaths_for_granule.py

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ cd C:\devpy\poswotdr\tasks\extract_filepaths_for_granule\test
(podr) λ pylint test_extract_file_paths_for_granule.py

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
1.  Use the test event in /tasks/extract_filepaths_for_granule/test/testevents/fixture2.json to test the lambda.
    This test event was created by taking the input to the lambda from the DrRecoveryWorkflowStateMachine, and
    a) replacing
    "cumulus_meta": {
        "state_machine": "arn:aws:states:us-west-2:065089468788:stateMachine:labCumulusDrRecoveryWorkflowStateMachine-aiTLe4uNdy0X",
        "message_source": "sfn",
    with:
    "cumulus_meta": {
        "task": "extract_filepaths_for_granule",
        "message_source": "local",

    b) removing these lines:
    "topic_arn": "arn:aws:sns:us-west-2:065089468788:lab-cumulus-sftrackerSns-1MMTZADVEIFUD",
    "workflow_tasks": {
      "Report": {
        "version": "1",
        "name": "lab-cumulus-SfSnsReport",
        "arn": "arn:aws:lambda:us-west-2:065089468788:function:lab-cumulus-SfSnsReport:SfSnsReport-282da1a3b4f8493441acc178396b846857bc1068"
      }
    },
```
<a name="pydoc"></a>
## pydoc extract_filepaths_for_granule
```
NAME
    extract_filepaths_for_granule - Name: extract_filepaths_for_granule.py

DESCRIPTION
    Description:  Lambda handler that extracts the keys for a granule's files from an input dict.

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
                                             'key': 'filepath1',
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
                    'filepaths' (list(string)): list of filepaths for the granule.

            Example:
                {"granules": [{"granuleId": "granxyz",
                             "filepaths": ["filepath1",
                                           "filepath2"]}]}

        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
```
