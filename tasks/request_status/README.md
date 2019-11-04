**Lambda function request_status **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_status](#pydoc-request-status)

<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/dr_dbutils folder to install dr_dbutils

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
Test files in the test folder that end with _postgres.py run
against a Postgres database in a Docker container, and allow you to 
develop against an actual database. You can create the database
using task/db_deploy. 
Note that these _postgres test files could use some more assert tests.
For now they can be used as a development aid. To run them you'll need to define
these 5 environment variables in a file named private_config.json, but do NOT check it into GIT. 
ex:
(podr2) λ cat private_config.json 
{"DATABASE_HOST": "db.host.gov_goes_here",
"DATABASE_PORT": "dbport_goes_here", 
"DATABASE_NAME": "dbname_goes_here", 
"DATABASE_USER": "dbusername_goes_here", 
"DATABASE_PW": "db_pw_goes_here"}

The remaining tests have everything mocked.

Run the tests:
C:\devpy\poswotdr\tasks\request_status  
λ activate podr
All tests:
(podr) λ nosetests -v

Individual tests (insert desired test file name):
(podr) λ nosetests test/test_requests_postgres.py -v

Code Coverage:
(podr) λ cd C:\devpy\poswotdr\tasks\request_status
(podr) λ nosetests --with-coverage --cover-erase --cover-package=request_status -v

Name                Stmts   Miss  Cover
---------------------------------------
request_status.py      75      0   100%
----------------------------------------------------------------------
Ran 10 tests in 10.656s
```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\request_status
(podr) λ pylint request_status.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_request_status.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/request_helpers.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
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
            DATABASE_HOST (string): the server where the database resides.
            DATABASE_PORT (string): the database port. The standard is 5432.
            DATABASE_NAME (string): the name of the database.
            DATABASE_USER (string): the name of the application user.
            DATABASE_PW (string): the password for the application user.

        Args:
            event (dict): A dict with zero or one of the following keys:

                granule_id (string): A granule_id to retrieve
                request_group_id (string): A request_group_id (uuid) to retrieve
                request_id (string): A request_id to retrieve
                object_key (string): An object_key to retrieve

                Examples: 
                    event: {"function": "query"}
                    event: {"function": "query",
                            "granule_id": "L0A_HR_RAW_product_0006-of-0420"
                           }
                    event: {"function": "query",
                            "request_id": "B2FE0827DD30B8D1"
                           }
                    event: {"function": "query",
                            "request_group_id": "e91ef763-65bb-4dd2-8ba0-9851337e277e"
                           }
                    event: {"function": "query",
                            "object_key": "L0A_HR_RAW_product_0006-of-0420.h5"
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
                        "request_id": "aa965db4-80af-4b05-b15c-4249dcbd3919",
                        "request_group_id": "79a1e2e9-cd92-48eb-87a3-c3cf932846c5",
                        "granule_id": "L0A_HR_RAW_product_0003-of-0420",
                        "object_key": "L0A_HR_RAW_product_0003-of-0420.h5",
                        "job_type": "restore",
                        "restore_bucket_dest": "sndbx-cumulus-glacier",
                        "archive_bucket_dest": "sndbx-cumulus-protected",
                        "job_status": "inprogress",
                        "request_time": "2019-10-23 18:24:38.370252+00:00",
                        "last_update_time": "2019-10-23 18:24:38.370252+00:00",
                        "err_msg": null
                    }
                ]

        Raises:
            BadRequestError: An error occurred parsing the input.
```
