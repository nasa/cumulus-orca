[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_status/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_status/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

**Lambda function request_status**

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_status](#pydoc-request-status)

## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  Configure a test event:
    name: QueryAll
    code: {"function": "query"}
    Save and execute it. If the database is empty, it will return [], otherwise it 
    should return all the requests.

2.  These are other valid test events:
    name: QueryByGranuleId
    code: {"function": "query", "granule_id": "your granule_id here"}

    name: QueryByRequestId
    code: {"function": "query", "request_id": "your request_id here"}

    name: QueryByRequestGroupId
    code: {"function": "query", "request_group_id": "your request_group_id here"}

    name: QueryByObjectKey
    code: {"function": "query", "object_key": "your object_key here"}
```
<a name="pydoc-request-status"></a>
## pydoc request_status
```
NAME
    request_status - Name: request_status.py

DESCRIPTION
    Description:  Queries the request_status table.

CLASSES
    builtins.Exception(builtins.BaseException)
        BadRequestError

    class BadRequestError(builtins.Exception)
        Exception to be raised if there is a problem with the request.

FUNCTIONS
    handler(event, context)
        Lambda handler. Retrieves job(s) from the database.

        Environment Vars:
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.

        Parameter Store:
            drdb-user-pass (string): the password for the application user (DATABASE_USER).
            drdb-host (string): the database host

        Args:
            event (dict): A dict with zero or one of the following keys:
                granule_id (string): A granule_id to retrieve
                request_group_id (string): A request_group_id (uuid) to retrieve
                request_id (string): A request_id to retrieve
                object_key (string): An object_key to retrieve

                Examples:
                    event: {'function': 'query'}
                    event: {'function': 'query',
                            'granule_id': 'L0A_HR_RAW_product_0006-of-0420'
                           }
                    event: {'function': 'query',
                            'request_id': 'B2FE0827DD30B8D1'
                           }
                    event: {'function': 'query',
                            'request_group_id': 'e91ef763-65bb-4dd2-8ba0-9851337e277e'
                           }
                    event: {'function': 'query',
                            'object_key': 'L0A_HR_RAW_product_0006-of-0420.h5'
                           }

            context (Object): None

        Returns:
            (list(dict)): A list of dict with the following keys:
                'request_id' (string): id uniquely identifying a table entry.
                'request_group_id' (string): The request_group_id the job belongs to.
                'granule_id' (string): The id of a granule.
                'object_key' (string): The name of the file that was requested.
                'job_type' (string): The type of job. "restore" or "regenerate"
                'restore_bucket_dest' (string): The bucket where the restored file will be put.
                'job_status' (string): The current status of the job
                'request_time' (string): UTC time that the request was initiated.
                'last_update_time' (string): UTC time of the last update to job_status.
                'err_msg' (string): Description of the error if the job_status is 'error'.

            Example:
                [
                    {
                        "request_id": "B2FE0827DD30B8D1",
                        "request_group_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
                        "granule_id": "granxyz",
                        "object_key": "my_test_filename",
                        "job_type": "restore",
                        "restore_bucket_dest": "my_test_bucket",
                        "job_status": "inprogress",
                        "request_time": "2019-09-30 18:24:38.370252+00:00",
                        "last_update_time": "2019-09-30 18:24:38.370252+00:00",
                        "err_msg": null
                    }
                ]

        Raises:
            BadRequestError: An error occurred parsing the input.
```
