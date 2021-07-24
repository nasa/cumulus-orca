[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/db_deploy/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/db_deploy/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for information on environment setup and testing.

# Lambda Function db_deploy

The **db_deploy** Lambda performs an install of ORCA objects into a PostgreSQL
database. The Lambda will check various attributes of the database and perform
either a fresh install of the ORCA schema, roes, users, and tables or a
migration from an older ORCA schema to the currently supported ORCA schema
version. This lambda is designed to run once during a terraform deployment of
the ORCA version.

The following sections going into more detail on utilizing this Lambda.

- [Testing db_deploy](#test-db_deploy) - Testing the lambda via unit and manual tests
- [Building db_deploy](#building-db_deploy) - Building the lambda and documentation.
- [Deploying db_deploy](#deploying-db_deploy) - Deploying and using the db_deploy lambda
- [db_deploy API Reference](#db_deploy-api-reference) - API reference


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

1. Make sure the following environment variables are set for the Lambda. The
   defaults are provided in parentheses.
   ```
   PREFIX           - Your var.prefix value from variables.tfvars
   AWS_REGION       - Your var.region value from variables.tfvars (us-west-2)
   DATABASE_PORT    = Your var.database_port value from variables.tfvars (5432)
   DATABASE_NAME    = Your var.database_name value from variables.tfvars (disaster_recovery)
   APPLICATION_USER = Your var.database_app_user value from variables.tfvars (orcauser)
   ROOT_USER        = "postgres"
   ROOT_DATABASE    = "postgres"
   ```
2. Create an empty JSON test event.
   ```
   {}
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


