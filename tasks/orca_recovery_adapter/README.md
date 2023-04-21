[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/orca_recovery_adapter/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/orca_recovery_adapter/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The `orca_recovery_adapter` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and recovers those files from their ORCA archive location. 

This lambda calls the ORCA recovery step-function synchronously, returning results and raising errors as appropriate.
This provides an injection seam to contact the ORCA recovery step-function with ORCA's formatting.

## Build

To build the **orca_recovery_adapter** lambda, run the `bin/build.sh` script from the
`tasks/orca_recovery_adapter` directory in a docker
container. The following shows setting up a container to run the script.

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
bash-4.2# cd tasks/orca_recovery_adapter/

# Run the tests
bash-4.2# bin/build.sh
```

### Testing orca_recovery_adapter

To run unit tests for **orca_recovery_adapter**, run the `bin/run_tests.sh` script from the
`tasks/orca_recovery_adapter` directory. Ideally, the tests should be run in a docker
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
bash-4.2# cd tasks/orca_recovery_adapter/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.

To run integration test for **orca_recovery_adapter**, run `bin/run_integration_tests.sh` script from the
`tasks/orca_recovery_adapter` directory. Make sure the object to be restored exists in ORCA before running the test.
Remember to export the following environment variables in your terminal before running the test.
- TODO

## Input

The `handler` function `handler(event, context)` expects input as a Cumulus Message. 
Event is passed from the AWS step function workflow. 
The actual format of that input may change over time, so we use the [cumulus-message-adapter](https://github.com/nasa/cumulus-message-adapter) package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

TODO: Example
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/input.json) for more information.

## Output

The `orca_recovery_adapter` lambda will request that files be restored from the ORCA archive.
See [recovery documentation](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/recovery-workflow) for more information.

TODO
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/output.json) for more information.

## Step Function Configuration

TODO
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/config.json) for more information.

## pydoc orca_recovery_adapter
[See the API documentation for more details.](API.md)