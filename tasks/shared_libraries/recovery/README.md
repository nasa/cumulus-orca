[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_database/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/recovery/requirements-dev.txt)

**Lambda function post_to_database **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Testing shared_recovery](#testing-shared_recovery) - Testing the library via unit tests
- [Building shared_recovery](#building-shared_recovery) - Building the library
- [Using shared_recovery](#using-shared_recovery) - Using the shared_recovery library in code.
- [pydoc recovery](#pydoc)

## Testing shared_recovery

There are several methods for testing **shared_recovery**. The various testing methods
are outlined in the sections below.


### Unit Testing shared_recovery

To run unit tests for **shared_recovery** run the `bin/run_tests.sh` script from the
`/tasks/shared_libraries/recovery` directory. Ideally, the tests should be run in a docker
container. The following shows setting up a container to run the tests.

```bash
# Invoke a docker container in interactive mode.
user$ docker run \
      -it \
      --rm \
      -v /path/to/cumulus-orca/repo:/data \
      amazonlinux:2 \
      /bin/bash

# Install the python development binaries
bash-4.2# yum install python3-devel

# In the container cd to /data
bash-4.2# cd /data

# Go to the task
bash-4.2# cd /tasks/shared_libraries/database/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.


## Building shared_recovery

Since the shared_recovery library is a single file there are no build steps for the
library.

Once the `API.md` file is created successfully, make sure to commit the file to
the repository.


## Using shared_recovery

To use the **shared_recovery** library in your lambda code base perform the following.

1. Keep in mind that the shared library is dependent upon the AWS reserved runtime environment variable [AWS_REGION](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html).

2. Install the necessary python libraries shown below.
   - boto3==1.12.47

3. Create an `orca_shared` directory and `__init__.py` dummy file.
   ```bash
   cd tasks/<your task name>
   mkdir orca_shared
   touch orca_shared/__init__.py
   ```
4. Copy the library file `shared_recovery.py` to the newly created `orca_shared`
   directory as seen below.
   ```bash
   cd tasks/<your task name>
   cp ../shared_libraries/database/shared_recovery.py orca_shared/
   ```
5. The library can now be used in your python code via a normal import per the
   examples seen below.
   ```python
   # Import the whole library
   from orca_shared import shared_recovery
   ```

### Integrating the Shared Library into Testing and Builds

When automating the use of this library it is recommended that the library is
imported into the lambda code base during testing and builds and not saved as
part of the lambda code base.

To automate the usage of this library during testing, it is recommended to add
code similar to the following to the `bin/run_tests.sh` script in your lambda
base directory.

```bash
echo "INFO: Copying ORCA shared libraries ..."
if [ -d orca_shared ]; then
    rm -rf orca_shared
fi

mkdir orca_shared
let return_code=$?
check_rc $return_code "ERROR: Unable to create orca_shared directory."

touch orca_shared/__init__.py
let return_code=$?
check_rc $return_code "ERROR: Unable to create [orca_shared/__init__.py] file"

cp ../shared_libraries/database/shared_recovery.py orca_shared/
let return_code=$?
check_rc $return_code "ERROR: Unable to copy shared library [orca_shared/shared_recovery.py]"

# Run tests and other stuff

# Cleanup shared libraries
rm -rf orca_shared
```

To automate the usage of this library during builds, it is recommended to add
code similar to the following to the `bin/build.sh` script in your lambda
base directory.

```bash
echo "INFO: Copying ORCA shared libraries ..."
if [ -d orca_shared ]; then
    rm -rf orca_shared
fi

mkdir -p build/orca_shared
let return_code=$?
check_rc $return_code "ERROR: Unable to create orca_shared directory."

touch build/orca_shared/__init__.py
let return_code=$?
check_rc $return_code "ERROR: Unable to create [orca_shared/__init__.py] file"

cp ../shared_libraries/database/shared_recovery.py build/orca_shared/
let return_code=$?
check_rc $return_code "ERROR: Unable to copy shared library [orca_shared/shared_recovery.py]"
```

<a name="pydoc"></a>
## pydoc recovery
```
Help on module shared_recovery:

NAME
    shared_recovery

DESCRIPTION
    Name: shared_recovery.py
    Description: Shared library that combines common functions and classes needed for recovery operations.

CLASSES
    enum.Enum(builtins.object)
        OrcaStatus
        RequestMethod
    
    class OrcaStatus(enum.Enum)
     |  OrcaStatus(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  Defines the status value used in the ORCA Recovery database for use by the recovery functions.
     |  
     |  Method resolution order:
     |      OrcaStatus
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  FAILED = <OrcaStatus.FAILED: 3>
     |  
     |  PENDING = <OrcaStatus.PENDING: 1>
     |  
     |  STAGED = <OrcaStatus.STAGED: 2>
     |  
     |  SUCCESS = <OrcaStatus.SUCCESS: 4>
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from enum.Enum:
     |  
     |  name
     |      The name of the Enum member.
     |  
     |  value
     |      The value of the Enum member.
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties inherited from enum.EnumMeta:
     |  
     |  __members__
     |      Returns a mapping of member name->value.
     |      
     |      This mapping lists all enum members, including aliases. Note that this
     |      is a read-only view of the internal mapping.
    
    class RequestMethod(enum.Enum)
     |  RequestMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  Provides potential actions for the database lambda to take when posting to the SQS queue.
     |  
     |  Method resolution order:
     |      RequestMethod
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  NEW_JOB = <RequestMethod.NEW_JOB: 'new_job'>
     |  
     |  UPDATE_FILE = <RequestMethod.UPDATE_FILE: 'update_file'>
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from enum.Enum:
     |  
     |  name
     |      The name of the Enum member.
     |  
     |  value
     |      The value of the Enum member.
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties inherited from enum.EnumMeta:
     |  
     |  __members__
     |      Returns a mapping of member name->value.
     |      
     |      This mapping lists all enum members, including aliases. Note that this
     |      is a read-only view of the internal mapping.

FUNCTIONS
    create_status_for_job(job_id: str, granule_id: str, archive_destination: str, files: List[Dict[str, Any]], db_queue_url: str)
        Creates status information for a new job and its files, and posts to queue.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            archive_destination: The S3 bucket destination of where the data is archived.
            files: A List of Dicts with the following keys:
                'filename' (str)
                'key_path' (str)
                'restore_destination' (str)
                'status_id' (int)
                'error_message' (str, Optional)
                'request_time' (str)
                'last_update' (str)
                'completion_time' (str, Optional)
            db_queue_url: The SQS queue URL defined by AWS.
    
    post_entry_to_queue(new_data: Dict[str, Any], request_method: shared_recovery.RequestMethod, db_queue_url: str) -> None
        Posts messages to an SQS queue.
        
        Args:
            new_data: A dictionary representing the column/value pairs to write to the DB table.
            request_method: The method action for the database lambda to take when posting to the SQS queue.
            db_queue_url: The SQS queue URL defined by AWS.
        
        Raises:
            None
    
    update_status_for_file(job_id: str, granule_id: str, filename: str, orca_status: shared_recovery.OrcaStatus, error_message: Union[str, NoneType], db_queue_url: str)
        Creates update information for a file's status entry, and posts to queue.
        Queue entry will be rejected by post_to_database if status for job_id + granule_id + filename does not exist.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            filename: The name of the file being copied.
            orca_status: Defines the status id used in the ORCA Recovery database.
            error_message: message displayed on error.
            db_queue_url: The SQS queue URL defined by AWS.

DATA
    Any = typing.Any
    Dict = typing.Dict
    List = typing.List
    Optional = typing.Optional
```