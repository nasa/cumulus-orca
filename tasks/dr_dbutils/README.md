**Lambda function request_files **

- [Setup](#setup)
- [Development](#development)
  * [Unit Testing and Coverage](#unit-testing-and-coverage)
  * [Linting](#linting)
- [Deployment](#deployment)
- [pydoc requests_db](#pydoc-requests-db)


<a name="setup"></a>
# Setup
    See the README in the tasks folder for general development setup instructions
    See the README in the tasks/pg_utils folder to install pg_utils

<a name="development"></a>
# Development

<a name="unit-testing-and-coverage"></a>
## Unit Testing and Coverage
```
Test files in the test folder that end with _postgres.py run
against a Postgres database in a Docker container, and allow you to 
develop against an actual database. You can create the database
using task/db_deploy. To run them you'll need to define
these 5 environment variables in a file named private_config.json, but do NOT check it into GIT. 
ex:
(podr2) λ cat tests/large_tests/private_config.json 
{"DATABASE_HOST": "db.host.gov_goes_here",
"DATABASE_PORT": "dbport_goes_here", 
"DATABASE_NAME": "dbname_goes_here", 
"DATABASE_USER": "dbusername_goes_here", 
"DATABASE_PW": "db_pw_goes_here"}

The remaining tests have everything mocked.

## Create docker container with DB for testing

`docker run -it --rm --name some-postgres -v /Users/<user>/cumulus-orca/database/ddl/base:/docker-entrypoint-initdb.d/ -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres`

*In another terminal:*

`docker run -it --rm --network host -e POSTGRES_PASSWORD=<new_password> postgres psql -h localhost -U postgres`

```
psql=# ALTER USER druser WITH PASSWORD 'new_password';
```

Once you've made these changes, update your `private_config.json` file with:

```json
{
    "DATABASE_USER": "druser",
    "DATABASE_PW": "<the value you added"
}

### Note that you have to use the druser account, otherwise the schema path won't quite match and you may receive errors like "table doesn't exist"

### Note that environment variable `PREFIX` is expected to be set for `get_dbconnect_info()`. This value is generally set in the lambdas that call this library.

Run the tests:
cd C:\devpy\poswotdr\tasks\dr_dbutils  
λ activate podr
All tests:
(podr) λ pytest

Individual tests (insert desired test file name):
(podr) λ pytest test/test_requests_postgres.py

Code Coverage:
(podr) λ cd C:\devpy\poswotdr\tasks\dr_dbutils
(podr) λ coverage run --source dr_dbutils -m pytest
(podr) λ coverage report

Name             Stmts   Miss  Cover
------------------------------------
requests_db.py     190      0   100%
----------------------------------------------------------------------
Ran 44 tests in 17.089s
```
<a name="linting"></a>
## Linting
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\dr_dbutils
(podr) λ pylint requests_db.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/request_helpers.py
 --------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_requests.py
 --------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_requests_postgres.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```
<a name="deployment"></a>
## Deployment
```
https://www.oreilly.com/library/view/head-first-python/9781491919521/ch04.html
Create the distribution file:
    (podr) λ cd C:\devpy\poswotdr\tasks\dr_dbutils
    (podr) λ py -3 setup.py sdist
    (podr) λ cd dist
    (podr) λ pip install dr_dbutils-1.0.tar.gz
 
```
<a name="pydoc-requests-db"></a>
## pydoc requests_db
```
NAME
    requests_db

DESCRIPTION
    This module exists to keep all database specific code for the request_status
    table in a single place.

CLASSES
    builtins.Exception(builtins.BaseException)
        BadRequestError
        DatabaseError
        NotFound

    class BadRequestError(builtins.Exception)
     |  Exception to be raised if there is a problem with the request.

    class DatabaseError(builtins.Exception)
     |  Exception to be raised when there's a database error.

    class NotFound(builtins.Exception)
     |  Exception to be raised when a request doesn't exist.

FUNCTIONS
    create_data(obj, job_type=None, job_status=None, request_time=None, last_update_time=None, err_msg=None)
        Creates a dict containing the input data for submit_request.

    delete_all_requests()
        Deletes everything from the request_status table.

        TODO: Currently this method is only used to facilitate testing,
        so unit tests may not be complete.

    delete_request(request_id)
        Deletes a job by request_id.

    get_all_requests()
        Returns all of the requests.

    get_job_by_request_id(request_id)
        Reads a row from request_status by request_id.

    get_jobs_by_granule_id(granule_id)
        Reads rows from request_status by granule_id.

    get_jobs_by_object_key(object_key)
        Reads rows from request_status by object_key.

    get_jobs_by_request_group_id(request_group_id)
        Returns rows from request_status for a request_group_id

    get_jobs_by_status(status, max_days_old=None)
        Returns rows from request_status by status, and optional days old

    get_utc_now_iso()
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    myconverter(obj)
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'

    request_id_generator()
        Returns a request_group_id (UUID) to be used to identify all the files for a granule
        ex. '0000a0a0-a000-00a0-00a0-0000a0000000'

    result_to_json(result_rows)
        Converts a database result to Json format

    submit_request(data)
        Takes the provided request data (as a dict) and attempts to update the
        database with a new request.

        Raises BadRequestError if there is a problem with the input.

    update_request_status_for_job(request_id, status, err_msg=None)
        Updates the status of a job.
              
```
