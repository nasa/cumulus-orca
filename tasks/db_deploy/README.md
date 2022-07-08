[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/db_deploy/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/db_deploy/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for information on environment setup and testing.

# Lambda Function db_deploy

The **db_deploy** Lambda performs an install of ORCA objects into a PostgreSQL
database. The Lambda will check various attributes of the database and perform
either a fresh install of the ORCA schema, roles, users, and tables or a
migration from an older ORCA schema to the currently supported ORCA schema
version. This lambda is designed to run once during a terraform deployment of
the ORCA version.

The following sections going into more detail on utilizing this Lambda.

- [Updating db_deploy](#updating-db_deploy) - Adding to and updating the lambda.
- [Testing db_deploy](#test-db_deploy) - Testing the lambda via unit and manual tests
- [Building db_deploy](#building-db_deploy) - Building the lambda and documentation.
- [Deploying db_deploy](#deploying-db_deploy) - Deploying and using the db_deploy lambda
- [db_deploy API Reference](#db_deploy-api-reference) - API reference


## Updating db_deploy

There are several areas to update when adding schema changes to the `db_deploy`
lambda. The layout, files, and methods to be aware of when adding migrations
to db_deploy are outlined below and consist of the following steps.

1. [Add the migration code](#adding-migration-code), sql, migration logic updates, and unit tests.
2. [Update the clean install](#updating-clean-install-code) sql, logic, and unit tests.
3. [Updatd the manual testing documentation](#updating-manual-testing).


### Adding Migration Code

When adding a new migration to db_deploy, there are certain naming and layout
conventions that should be followed. In addition there are several files that
should be updated so that the migration code can be ran properly. The steps
below will guide you through the files that need to be touched and the naming
standards expected.

1. **Create the migration directories.** Migrations in db_deploy are located
   under the `migrations` folder and follow a naming convention of
   *migrate_versions_x_to_y* where x is the current version of the schema and y
   is the new schema version. An identical folder should also be created under
   the `test/unit_tests/migrations` directory. An example can be seen below. Note
   that schema versions do not equate to ORCA application version and do not use
   semantic versioning but are an increasing integer.
   ```bash
   mkdir -p migrations/migrate_versions_4_to_5
   mkdir -p test/unit_tests/migrations/migrate_versions_4_to_5
   ```
2. **Create the migration files in the new migration directories.** Once the
   migration directory is created, create a `migrate.py` and `migrate_sql.py`
   file within the directory. Add corresponding `test_migrate_vY.py` and
   `test_migrate_sql_vY.py` files in the test migration directory. An example can
   be seen below. The `migrate.py` file should include a function with the
   following naming convention and signature
   `def migrate_versions_x_to_y(config: Dict[str, str], is_latest_version: bool, *args)`
   this function should run the migration SQL in the proper order to perform a
   migration from version x to version y. The `migrate_sql.py` file should have
   the SQL needed to perform the migration. See previous versions for examples
   on how the SQL should be formatted and expressed in functions. The unit test
   files `test_migrate_vy.py` and `test_migrate_sql_vy.py` should contain unit
   tests for all code written.
   ```bash
   touch migrations/migrate_versions_x_to_y/migrate.py
   touch migrations/migrate_versions_x_to_y/migrate_sql.py
   touch test/unit_tests/migrations/migrate_versions_x_to_y/test_migrate_vy.py
   touch test/unit_tests/migrations/migrate_versions_x_to_y/test_migrate_sql_vy.py
   ```
3. **Update the `migrate_db.py` file.** Within the `migrations/migrate_db.py`
   file, the `perform_migrations` function logic must be updated to include
   the new migration. A typical logic update can be seen below. Note that any
   additional arguments needed by migration will need to be expressed in the
   `perform_migration` function as inputs.
   ```bash
   from migrations.migrate_versions_4_to_5.migrate import migrate_versions_4_to_5

   def perform_migration(
    current_schema_version: int, config: Dict[str, str], orca_buckets: List[str]
) -> None:
       ...

       if current_schema_version == 4:
           # Run migrations from version 4 to version 5
           migrate_versions_4_to_5(config, True, orca_buckets)
           current_schema_version = 5
   ```
4. **Update the `db_deploy.py` file.** Within the `db_deploy.py` file, update the
   `LATEST_ORCA_SCHEMA_VERSION` value to the new version number `Y`. Make
   additional updates as needed for inputs needed by the migration scripts.


### Updating Clean Install Code

In addition to writing the migration code, the code for a clean install must also
be updated. It is recommended that since the clean install code is an approximate
duplication of the migration code, that updates to this code occur after the
migration SQL and install have been properly vetted. The steps below provide some
broad guidance on updating the clean install code.

1. **Update the `orca_sql.py` file.** In the `install/orca_sql.py` file, add any
   new objects created by the migration. The code can often be copied directly
   from the `migrate_sql.py` directly. Update the definitions of current objects
   modified by the migration to present the proper end state for the latest
   version. It is recommended to arrange the SQL into proper schema sections based
   on application database and application logic.
2. **Update the `create_db.py` file.** In the `install/create_db.py` file, update
   the logic to create any new objects. This may require updates to existing
   functions, or creation of new functions if the objects are a part of a new
   schema.
3. **Update the `db_deploy.py` file.** Make updates to the `db_deploy.py`
   function call `create_fresh_orca_install` if needed.


### Updating Manual Testing

All migration changes should be manually tested to verify that the proper changes
occur and that the SQL is well formed. Run the tests outlined in the manual
testing document. Add additional tests as needed to interrogate the migration
objects, and update the examples and outputs to match the latest version changes.
In addition, update the manual test helper scripts and instructions as needed
based on testing needs.


## Testing db_deploy

There are several methods for testing **db_deploy**. The various testing methods
are outlined in the sections below.


### Unit Testing db_deploy

To run unit tests for **db_deploy** run the `bin/run_tests.sh` script from the
`tasks/db_deploy` directory. Ideally, the tests should be run in a docker
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
bash-4.2# cd tasks/db_deploy/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.


### Manually Testing db_deploy

To manually test the db_deploy application against a real database, follow the
instructions laid out in the [manual test documentation](test/manual_tests/README.md).


### Integration Testing of db_deploy

To perform integration testing, make sure version 2.0.1 or older of the ORCA
module is installed into your Cumulus instance and several recovery jobs have
been run and are in various states (pending, error, complete). Status values
may have to be manipulated in the PostgreSQL database to achieve a full test.

Upload the latest version of the **db_deploy** Lambda code to AWS using the
AWS CLI `aws lambda update-function-code --function-name <prefix>_db_deploy --zip-file fileb://db_deploy.zip --profile <profile-name>`.

Using the AWS Lambda interface for db_deploy perform the following steps:

1. Make sure the following environment variable is set for the Lambda.
   ```
   DB_CONNECT_INFO_SECRET_ARN   - Your secretsmanager secret ARN needed for connecting to the DB.
   AWS_REGION       - automatically set by AWS as a defined runtime variable
   ```
2. Create a JSON test event as shown below. Replace `prefix` with the one you used.
   ```json
   {
   "orcaBuckets": ["prefix-orca-primary"]
   }  
   ```
3. Perform validation of the migration similar to the tests and commands provided
   in the [manual test documentation](test/manual_tests/README.md) for validating
   a migration.
4. Check the Lambda logs and error messages in CloudWatch.


## Building db_deploy

To build the db_deploy API documentation and lambda zip file use the provided
scripts. Information on the scripts is provided in the following sections.

### Building API documentation

To build the lambda API documentation, run the `bin/build_doc.sh` script from the
`tasks/db_deploy` directory. Ideally, the build document should be run in the
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
bash-4.2# cd tasks/db_deploy/

# Run the build
bash-4.2# bin/build_doc.sh
```

Once the `API.md` file is created successfully, make sure to commit the file to
the repository.


### Building the Lambda zip file

To build the lambda, run the `bin/build.sh` script from the `tasks/db_deploy`
directory. Ideally, the build should be run in the same docker container as tests.

```bash
# Invoke a docker container in interactive mode.
user$ docker run \
      -it \
      --rm \
      -v /path/to/cumulus-orca/repo:/data \
      maven.earthdata.nasa.gov/aws-sam-cli-build-image-python3.8:latest \
      /bin/bash

# In the container cd to /data
bash-4.2# cd /data

# Go to the task
bash-4.2# cd tasks/db_deploy/

# Run the build
bash-4.2# bin/build.sh
```

Note that Bamboo will run this same script via the `bin/build_tasks.sh` script found
in the cumulus-orca base of the repo.


## Deploying db_deploy

Generally **db_deploy** should be deployed as part of the ORCA terraform
deployment. The deployment can be done manually by using the AWS CLI to upload
the zip file created in the [build step](#building-the-lambda-zip-file) with the
proper variables. See the [integation testing section](#integration-testing-of-db_deploy)
of this document for more information on validating the deployment.


## db_deploy API Reference

API reference information is available in the [API Reference documentation.](API.md).