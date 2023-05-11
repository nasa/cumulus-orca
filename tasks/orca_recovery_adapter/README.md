[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/orca_recovery_adapter/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/orca_recovery_adapter/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The `orca_recovery_adapter` module is meant to be deployed as a lambda function that takes a Cumulus message, 
extracts a list of files, and initiates recovery of those files from their ORCA archive location. 

This lambda calls the ORCA recovery step-function, returning results and raising errors as appropriate.
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
- TODO: https://bugs.earthdata.nasa.gov/browse/ORCA-666

## Environment Variables

See [API.md](API.md#handler)

## Input

The `handler` function `handler(event, context)` expects input as a Cumulus Message. 
Event is passed from the AWS step function workflow. 
The actual format of that input may change over time, so we use the [cumulus-message-adapter](https://github.com/nasa/cumulus-message-adapter) package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

```json
{
  "payload": {
    "granules": [
      {
        "granuleId": "a3a94886-c11d-4c21-a942-a836b8e9aa75",
        "version": "integrationGranuleVersion",
        "files": [
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
            "bucket": "PREFIX-orca-primary"
          }
        ]
      }
    ]
  },
  "task_config": {
    "buckets": "{$.meta.buckets}",
    "fileBucketMaps": "{$.meta.collection.files}",
    "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
    "asyncOperationId": "{$.cumulus_meta.asyncOperationId}",
    "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
    "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}",
    "defaultRecoveryTypeOverride": "{$.meta.collection.meta.orca.defaultRecoveryTypeOverride}"
  }
  ,
  "meta": {
    "buckets": {
      "protected": {"name": "PREFIX-protected", "type": "protected"},
      "internal": {"name": "PREFIX-internal", "type": "internal"},
      "private": {"name": "PREFIX-private", "type": "private"},
      "public": {"name": "PREFIX-public", "type": "public"},
      "orca_default": {"name": "PREFIX-orca-primary", "type": "orca"}
    },
    "collection": {
      "meta": {
        "orca": {
          "excludedFileExtensions": [".blah"]
        }
      },
      "files": [
        {
          "regex": ".*.tar.gz",
          "sampleFileName": "blah.tar.gz",
          "bucket": "public"
        },
        {
          "regex": ".*.jpg",
          "sampleFileName": "blah.jpg",
          "bucket": "public"
        },
        {
          "regex": ".*.hdf",
          "sampleFileName": "blah.hdf",
          "bucket": "public"
        }
      ]
    }
  },
  "cumulus_meta": {
    "system_bucket": "PREFIX-internal"
  }
}
```

See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/input.json) for more information.

## Output

The `orca_recovery_adapter` lambda will request that files be restored from the ORCA archive.
See [recovery documentation](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/recovery-workflow) for more information.

```json
{
  "payload": {
    "granules": [{
      "granuleId": "a3a94886-c11d-4c21-a942-a836b8e9aa75", 
      "keys": [{
        "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "destBucket": "doctest-public"
      }], 
      "recoverFiles": [{
        "success": true, 
        "filename": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "restoreDestination": "doctest-public", 
        "s3MultipartChunksizeMb": null, 
        "statusId": 1, 
        "requestTime": "2023-05-08T16:59:01.910817+00:00", 
        "lastUpdate": "2023-05-08T16:59:01.910817+00:00"}]
    }], 
    "asyncOperationId": "dd57408f-8602-4601-bee7-04062444250e"
  }, 
  "task_config": {
    "buckets": "{$.meta.buckets}", 
    "fileBucketMaps": "{$.meta.collection.files}", 
    "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}", 
    "asyncOperationId": "{$.cumulus_meta.asyncOperationId}", 
    "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}", 
    "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}", 
    "defaultRecoveryTypeOverride": "{$.meta.collection.meta.orca.defaultRecoveryTypeOverride}"
  }, 
  "meta": {
    "buckets": {
      "protected": {"name": "doctest-protected", "type": "protected"}, 
      "internal": {"name": "doctest-internal", "type": "internal"}, 
      "private": {"name": "doctest-private", "type": "private"}, 
      "public": {"name": "doctest-public", "type": "public"}, 
      "orca_default": {"name": "doctest-orca-primary", "type": "orca"}
    },
    "collection": {
      "meta": {
        "orca": {
          "excludedFileExtensions": [".blah"]
        }
      }, 
      "files": [
        {"regex": ".*.tar.gz", "sampleFileName": "blah.tar.gz", "bucket": "public"}, 
        {"regex": ".*.jpg", "sampleFileName": "blah.tar.gz", "bucket": "public"}, 
        {"regex": ".*.hdf", "sampleFileName": "blah.tar.gz", "bucket": "public"}
      ]
    }},
  "cumulus_meta": {"system_bucket": "doctest-internal"}, 
  "exception": "None"
}
```

See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/output.json) for more information.

## Step Function Configuration

As part of the [Cumulus Message Adapter configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration), 
several properties must be passed into the lambda.
See [input](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/input.json) 
and [config](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/config.json) 
schemas for more information.

```
{
  "Comment": "Recover files belonging to a granule",
  "StartAt": "OrcaRecovery",
  "TimeoutSeconds": 18000,
  "States": {
    "OrcaRecovery": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "ReplaceConfig": {
            "FullMessage": true
          },
          "task_config": {
            "buckets": "{$.meta.buckets}",
            "fileBucketMaps": "{$.meta.collection.files}",
            "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
            
            "asyncOperationId": "{$.cumulus_meta.asyncOperationId}",
            "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
            "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}",
            "defaultRecoveryTypeOverride": "{$.meta.collection.meta.orca.defaultRecoveryTypeOverride}"
          }
        }
      },
      "Type": "Task",
      "Resource": "${orca_lambda_recovery_adapter_arn}",
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
    },
    "WorkflowFailed": {
      "Type": "Fail",
      "Cause": "Workflow failed"
    }
  }
}
```

See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/config.json) for more information.

## pydoc orca_recovery_adapter
[See the API documentation for more details.](API.md)