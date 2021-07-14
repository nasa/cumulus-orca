[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/shared_libraries/database/database/requirements-dev.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/database/requirements-dev.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for information on environment setup and testing.

# Shared Library shared_db

The **shared_db** library contains several functions for connecting to a database.

The following sections going into more detail on utilizing this Lambda.

- [Testing shared_db](#testing-shared_db) - Testing the library via unit tests
- [Building shared_db](#building-shared_db) - Building the library
- [Using shared_db](#using-shared_db) - Using the shared_db library in code.
- [shared_db API Reference](#shared_db-api-reference) - API refrence


## Testing shared_db

There are several methods for testing **shared_db**. The various testing methods
are outlined in the sections below.


### Unit Testing shared_db

To run unit tests for **shared_db** run the `bin/run_tests.sh` script from the
`/tasks/shared_libraries/database` directory. Ideally, the tests should be run in a docker
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


## Building shared_db

Since the shared_db library is a single file there are no build steps for the
library.

To build the shared_db API documentation, run the `bin/build_doc.sh` script from the
`tasks/shared_libraries/database` directory. Ideally, the build document should be run in the
same docker container as tests.

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
bash-4.2# cd tasks/shared_libraries/database

# Run the build
bash-4.2# bin/build_doc.sh
```

Once the `API.md` file is created successfully, make sure to commit the file to
the repository.


## Using shared_db

To use the **shared_db** library in your lambda code base perform the following.

1. Install the necessary python libraries shown below.
   - boto3==1.12.49
   - cumulus-message-adapter==1.3.0
   - cumulus-message-adapter-python==1.2.1
   - SQLAlchemy==1.4.11
   - *psycopg2-binary==2.8.6* - For development work only.
   - *AWS psycopg2 Lambda Library* - For builds and creating a zip file for Lambda deploys.

2. Create an `orca_shared` directory and `__init__.py` dummy file.
   ```bash
   cd tasks/<your task name>
   mkdir orca_shared
   touch orca_shared/__init__.py
   ```
3. Copy the library file `shared_db.py` to the newly created `orca_shared`
   directory as seen below.
   ```bash
   cd tasks/<your task name>
   cp ../shared_libraries/database/shared_db.py orca_shared/
   ```
4. The library can now be used in your python code via a normal import per the
   examples seen below.
   ```python
   # Import the whole library
   from orca_shared import shared_db

   # Import specific functions
   from orca_shared.shared_db import get_configuration, get_admin_connection, get_user_connection
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

cp ../shared_libraries/database/shared_db.py orca_shared/
let return_code=$?
check_rc $return_code "ERROR: Unable to copy shared library [orca_shared/shared_db.py]"

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

cp ../shared_libraries/database/shared_db.py build/orca_shared/
let return_code=$?
check_rc $return_code "ERROR: Unable to copy shared library [orca_shared/shared_db.py]"
```


### Important Notes About Using and Deploying the Library

Note that the library relies on external items like the environment and AWS
SecretsManager to get the proper values for creating the connection strings.

When using this shared library in your code, the following environment
variables must be set as part of your terraform configuration for your lambda.
The table below provides information on the variables that should be set along
with the ORCA terraform variable to use when setting them in your terraform code
in the environment block. Note that some variables are OPTIONAL.

| Name             | Description                                                            | Terraform Variable    | Example Value |
| ---------------- | ---------------------------------------------------------------------- | --------------------- | -------------     |
| PREFIX           | Deployment prefix used to pull the proper AWS secret.                  | var.prefix            | dev               |
| AWS_REGION       | AWS reserved runtime variable used to set boto3 client region.         | Set by AWS            | us-west-2         |
| DATABASE_PORT    | The database port. The standard is 5432                                | var.database_port     | 5432              |
| DATABASE_NAME    | The name of the application database.                                  | var.database_name     | disaster_recovery |
| APPLICATION_USER | The name of the database application user.                             | var.database_app_user | orcauser          |
| ADMIN_USER       | *OPTIONAL* The name of the database super user.             | Set to "postgres"     | postgres          |
| ADMIN_DATABASE   | *OPTIONAL* The name of the admin database for the instance. | Set to "postgres"     | postgres          |

The following is an example of the minimum environment variables that must be
set as part of your terraform lambda environment configuration.

```yaml
  environment {
    variables = {
      PREFIX           = var.prefix
      DATABASE_PORT    = var.database_port
      DATABASE_NAME    = var.database_name
      APPLICATION_USER = var.database_app_user
    }
```

**IMPORTANT**: The *AWS_REGION* variable is set at runtime by AWS. This variable
does not need to be added to your terraform configuration. However, any unit
tests that call `get_configuration` that are not mocked will need to have the
environment variable set. This is to satisfy a boto3 client requirement where
AWS region must be set.

In addition to the environment, the following SecretsManager stores must be
available. The ORCA terraform deployment should create them for you. Note that
\<prefix\> is the value of the `var.prefix` variable from the terraform
configuration.

- \<prefix\>-drdb-user-pass (string): The password for the application user (APPLICATION_USER).
- \<prefix\>-drdb-host (string): The database host.
- \<prefix\>-drdb-admin-pass: The password for the admin user


## shared_db API Reference

API reference information is available in the [API Reference documentation.](API.md).


