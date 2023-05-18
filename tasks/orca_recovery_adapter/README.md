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
In addition to the [standard environment variables](#lambda-setup),
export the following environment variables in your terminal before running the test.
- ORCA_RECOVERY_BUCKET - S3 bucket where the object is stored in ORCA. For example, `test-orca-primary`.
- CUMULUS_BUCKET_NAME - S3 bucket where the object will be recovered to. For example, `test-public`.
- CUMULUS_SYSTEM_BUCKET_NAME - S3 bucket used by CMA. For example, `test-internal`.
- OBJECT_KEY_NAME - The S3 object url. For example, `MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf`.
- GRANULE_ID - The Cumulus Granule ID of the granule containing the file to be recovered.

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

This is what the same input looks like for use with the [Step Function configuration](#step-function-configuration):

```json
{
  "payload": {
    "granules": [
      {
        "granuleId": "a3a94886-c11d-4c21-a942-a836b8e9aa75",
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
          "sampleFileName": "blah.tar.gz",
          "bucket": "public"
        },
        {
          "regex": ".*.hdf",
          "sampleFileName": "blah.tar.gz",
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
Note that if a [Step Function](#step-function-configuration) is used, the output may be obfuscated and stored in S3 by CMA.

```json
{
  "payload": {
    "granules": [{
      "granuleId": "a3a94886-c11d-4c21-a942-a836b8e9aa75", 
      "keys": [{
        "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "destBucket": "PREFIX-public"
      }], 
      "recoverFiles": [{
        "success": true, 
        "filename": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf", 
        "restoreDestination": "PREFIX-public", 
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
        {"regex": ".*.tar.gz", "sampleFileName": "blah.tar.gz", "bucket": "public"}, 
        {"regex": ".*.jpg", "sampleFileName": "blah.tar.gz", "bucket": "public"}, 
        {"regex": ".*.hdf", "sampleFileName": "blah.tar.gz", "bucket": "public"}
      ]
    }},
  "cumulus_meta": {"system_bucket": "PREFIX-internal"}, 
  "exception": "None"
}
```

See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/output.json) for more information.

## Lambda Setup
- Create a new lambda in AWS with a `Python` runtime.
- Assign the lambda an IAM role that has [StartExecution](https://docs.aws.amazon.com/step-functions/latest/apireference/API_StartExecution.html)
  permissions on the recovery Step Function.
- Set the environment variable `ORCA_RECOVERY_STEP_FUNCTION_ARN` to the `orca_sfn_recovery_workflow_arn` output from ORCA.

## Step Function Configuration

For minimum impact to integrators, it may be best to run the adapter lambda via a Step Function,
mirroring how integrators call the ORCA Recovery Workflow via its Step Function.
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
    "OrcaRecoveryAdapter": {
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
      "Next": "WorkflowSucceeded"
    },
    "WorkflowFailed": {
      "Type": "Fail",
      "Cause": "Workflow failed"
    },
    "WorkflowSucceeded": {
      "Type": "Succeed"
    }
  }
}
```

See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/orca_recovery_adapter/schemas/config.json) for more information.

## pydoc orca_recovery_adapter
[See the API documentation for more details.](API.md)