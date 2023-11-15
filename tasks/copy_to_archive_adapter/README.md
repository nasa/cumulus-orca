[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_archive_adapter/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_archive_adapter/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

::important
This adapter was created as a proof of concept and should not be used by end users. Use [Cumulus copy_to_archive_adapter](https://github.com/nasa/cumulus/tree/master/tasks/orca-copy-to-archive-adapter) instead.
:::

Since ORCA is decoupling from Cumulus starting in ORCA v8.0, users will now run the same [ORCA `copy_to_archive` workflow](https://github.com/nasa/cumulus-orca/tree/master/modules/workflows/OrcaCopyToArchiveWorkflow) but must need to update the existing workflow configuration to point to Cumulus[copy_to_archive_adapter lambda](https://github.com/nasa/cumulus/tree/master/tasks/orca-copy-to-archive-adapter) which then runs our existing `copy_to_archive` lambda.

:::note
Make sure to replace `<CUMULUS_COPY_TO_ARCHIVE_ADAPTER_ARN>` under `Resource` property below. See [cumulus terraform modules](https://github.com/nasa/cumulus/blob/master/tf-modules/cumulus/outputs.tf#L86) for additional details on how to add this.
:::

```json
"CopyToArchive":{
  "Parameters":{
    "cma":{
      "event.$":"$",
      "task_config": {
        "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
        "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
        "providerId": "{$.meta.provider.id}",
        "providerName": "{$.meta.provider.name}",
        "executionId": "{$.cumulus_meta.execution_name}",
        "collectionShortname": "{$.meta.collection.name}",
        "collectionVersion": "{$.meta.collection.version}",
        "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"
      }
    }
  }
},
  "Type":"Task",
  "Resource":"<CUMULUS_COPY_TO_ARCHIVE_ADAPTER_ARN>",
  "Catch":[
    {
      "ErrorEquals":[
        "States.ALL"
      ],
      "ResultPath":"$.exception",
      "Next":"WorkflowFailed"
    }
  ],
  "Retry": [
    {
      "ErrorEquals": [
        "States.ALL"
      ],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2
    }
  ],
  "Next":"WorkflowSucceeded"
},
```

## Exclude files by extension.

You are able to specify a list of file types (extensions) that you'd like to exclude from the backup/copy_to_archive functionality. This is done on a per-collection basis, configured in the Cumulus collection configuration under the `meta.orca.excludedFileExtensions` key:

```json
"collection": {
    "meta": {
        "orca": {
            "excludedFileExtensions": [".xml", ".cmr", ".cmr.xml"]
        }
    }
}
```

Note that this must be done for _each_ collection configured. If this list is empty or not included in the meta configuration, the `copy_to_archive` function will include files with all extensions in the backup.

## Build

To build the **copy_to_archive_adapter** lambda, run the `bin/build.sh` script from the
`tasks/copy_to_archive_adapter` directory in a docker
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
bash-4.2# cd tasks/copy_to_archive_adapter/

# Run the tests
bash-4.2# bin/build.sh
```

### Testing copy_to_archive_adapter

To run unit tests for **copy_to_archive_adapter**, run the `bin/run_tests.sh` script from the
`tasks/copy_to_archive_adapter` directory. Ideally, the tests should be run in a docker
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
bash-4.2# cd tasks/copy_to_archive_adapter/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.

To run integration test for **copy_to_archive_adapter**, run `bin/run_integration_tests.sh` script from the
`tasks/copy_to_archive_adapter` directory. Make sure the object to be copied exists in the source bucket first before running the test.
Remember to export the following environment variables in your terminal before running the test.
- ORCA_RECOVERY_BUCKET - S3 bucket where the object should be recovered. For example, `test-orca-primary`.
- CUMULUS_BUCKET_NAME - S3 bucket where the object to be recovered exists. For example, `orca-sandbox-s3-provider`.
- OBJECT_KEY_NAME - The S3 object url. For example, `MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf`.

## Environment Variables

See [API.md](API.md#handler)

## Input

The `handler` function `handler(event, context)` expects input as a Cumulus Message. 
Event is passed from the AWS step function workflow. 
The actual format of that input may change over time, so we use the [cumulus-message-adapter](https://github.com/nasa/cumulus-message-adapter) package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

The `copy_to_archive_adapter` lambda function expects that the input payload has a `granules` object, similar to the output of `MoveGranulesStep`:

```json
{
  "payload": {
    "granules": [
      {
        "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
        "dataType": "MOD09GQ",
        "version": "006",
        "createdAt": 628021800000,
        "files": [
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318361000,
            "bucket": "orca-sandbox-protected",
            "url_path": "MOD09GQ/006/",
            "type": "",
            "source": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "duplicate_found": true
          },
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318366000,
            "bucket": "orca-sandbox-private",
            "url_path": "MOD09GQ/006",
            "type": "",
            "source": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "duplicate_found": true
          },
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318372000,
            "bucket": "orca-sandbox-public",
            "url_path": "MOD09GQ/006",
            "type": "",
            "source": "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "duplicate_found": true
          },
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "bucket": "orca-sandbox-private",
            "source": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "type": "metadata",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "url_path": "MOD09GQ/006"
          }
        ],
        "sync_granule_duration": 1728
      }
    ]
  }
}
```
From the json file, the `filepath` shows the current S3 location of files that need to be copied over to archive bucket such as `"filename": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf"`.
**Note:** We suggest that the `copy_to_archive_adapter` task be placed any time after the `MoveGranulesStep`. It will propagate the input `granules` object as output, so it can be used as the last task in the workflow.
See the schema [input file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive_adapter/schemas/input.json) for more information.


## Output

The `copy_to_archive` lambda will, as the name suggests, copy a file from its current source destination. The destination location is defined as 
`${archive_bucket}/${filepath}`, where `${archive_bucket}` is pulled from the environment variable `ORCA_DEFAULT_BUCKET` and `${filepath}` is pulled from the Cumulus granule object input.

The output of this lambda is a dictionary with a `granules` and `copied_to_orca` attributes.  See the schema [output file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive_adapter/schemas/output.json) for more information. Below is an example of the output:

```json
{
	"granules": [
    {
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "dataType": "MOD09GQ",
      "version": "006",
      "createdAt": 628021800000,
      "files": [
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318366000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006/",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        },
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318366000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        },
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318372000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        }
      ],
      "sync_granule_duration": 1676
    }
  ],
	"copied_to_orca": [
      "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
      "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml"
  ]
}
```

## Step Function Configuration

As part of the [Cumulus Message Adapter configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration) 
for `copy_to_archive`, the `excludedFileExtensions`, `s3MultipartChunksizeMb`, `providerId`, `executionId`, `collectionShortname`, `collectionVersion`, `defaultBucketOverride`, and `defaultStorageClassOverride` keys must be present under the 
`task_config` object as seen below. 
Per the [config schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive_adapter/schemas/config.json), 
the values of the keys are used the following ways. 
The `provider` key should contain an `id` key that returns the provider id from Cumulus. 
The `cumulus_meta` key should contain an `execution_name` key that returns the step function execution ID from AWS. 
The `collection` key value should contain a `name` key and a `version` key that return the required collection shortname and collection version from Cumulus respectively.
The `collection` key value should also contain a `meta` key that includes an `orca` key having an optional `excludedFileExtensions` key that is used to determine file patterns that should not be 
sent to ORCA. In addition, the `orca` key also contains optional `defaultBucketOverride` key that overrides the `ORCA_DEFAULT_BUCKET` set on deployment and optional `defaultStorageClassOverride` key that overrides the storage class to use when storing files in Orca. 
The optional `s3MultipartChunksizeMb` is used to override the default setting for the lambda s3 copy maximum multipart chunk size value when copying large files to ORCA.
These settings can often be derived from the collection configuration in Cumulus as seen below:

```
{
  "States": {
    "CopyToArchive": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "task_config": {
            "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}",
            "excludedFileExtensions": "{$.meta.collection.meta.orca.excludedFileExtensions}",
            "providerId": "{$.meta.provider.id}",
            "providerName": "{$.meta.provider.name}",
            "executionId": "{$.cumulus_meta.execution_name}",
            "collectionShortname": "{$.meta.collection.name}",
            "collectionVersion": "{$.meta.collection.version}",
            "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"
          }
        }
      },
      "Type": "Task",
      "Resource": "${orca_lambda_copy_to_archive_adapter_arn}",
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
      ]
    }
  }
}
```
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive_adapter/schemas/config.json) for more information.

## pydoc copy_to_archive_adapter
[See the API documentation for more details.](API.md)