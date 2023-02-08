[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_archive/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The `copy_to_archive` module is a lambda function that takes a message, extracts a list of files, and copies those files from their current storage location into an ORCA archive bucket. 
It also sends additional metadata attributes to metadata SQS queue needed for Cumulus reconciliation.


## Exclude files by extension.

You are able to specify a list of file types (extensions) that you'd like to exclude from the backup/copy_to_archive functionality. This is done on a per-collection basis, configured in the Cumulus collection configuration under the `meta.orca.excludedFileExtensions` key:

```json
      "collection": {
        "meta": {
            "orca":{
                "excludedFileExtensions": [".xml", ".cmr", ".cmr.xml"]
            }
        }

```

Note that this must be done for _each_ collection configured. If this list is empty or not included in the meta configuration, the `copy_to_archive` function will include files with all extensions in the backup.


## Build

To build the **copy_to_archive** lambda, run the `bin/build.sh` script from the
`tasks/copy_to_archive` directory in a docker
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
bash-4.2# cd tasks/copy_to_archive/

# Run the tests
bash-4.2# bin/build.sh
```

### Testing copy_to_archive

To run unit tests for **copy_to_archive**, run the `bin/run_tests.sh` script from the
`tasks/copy_to_archive` directory. Ideally, the tests should be run in a docker
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
bash-4.2# cd tasks/copy_to_archive/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.

## Deployment

The `copy_to_archive` lambda function can be deployed using terraform using the example shown in  `"aws_lambda_function" "copy_to_archive"` resource block of `modules/lambdas/main.tf` file.

## Input

The `handler` function `handler(event, context)` expects input as a Cumulus Message. Event is passed from the AWS step function workflow.

The `copy_to_archive` lambda function expects that the input has a `granules` object, similar to the output of `MoveGranulesStep`:

```json
{
  "input": {
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
**Note:** We suggest that the `copy_to_archive` task be placed any time after the `MoveGranulesStep`. It will propagate the input `granules` object as output, so it can be used as the last task in the workflow.
See the schema [input file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive/schemas/input.json) for more information.


## Output

The `copy_to_archive` lambda will, as the name suggests, copy a file from its current source destination. The destination location is defined as 
`${archive_bucket}/${filepath}`, where `${archive_bucket}` is pulled from the environment variable `ORCA_DEFAULT_BUCKET` and `${filepath}` is pulled from the Cumulus granule object input.

The output of this lambda is a dictionary with a `granules` and `copied_to_orca` attributes.  See the schema [output file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive/schemas/output.json) for more information. Below is an example of the output:

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

## Configuration

The `providerId`, `executionId`, `collectionShortname`, and `collectionVersion` and keys must be present under the 
`config` object as seen below, 
while the `excludedFileExtensions`, `s3MultipartChunksizeMb`, `providerName`, `defaultBucketOverride`, and `defaultStorageClassOverride` are stored as paths, and will be retrieved in-code.
Per the [config schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive/schemas/config.json), 
the values of the keys are used the following ways. The `provider` key should contain an `id` key that returns the provider id from Cumulus. The `cumulus_meta` key should contain an `execution_name` key that returns the step function execution ID from AWS. 
The `collection` key value should contain a `name` key and a `version` key that return the required collection shortname and collection version from Cumulus respectively.
The `collection` key value should also contain a `meta` key that includes an `orca` key having an optional `excludedFileExtensions` key that is used to determine file patterns that should not be 
sent to ORCA.
The `orca` key also contains optional `defaultBucketOverride` key that overrides the `ORCA_DEFAULT_BUCKET` set on deployment,
and the optional `defaultStorageClassOverride` key that overrides the storage class to use when storing files in Orca.
The optional `s3MultipartChunksizeMb` is used to override the default setting for the lambda s3 copy maximum multipart chunk size value when copying large files to ORCA.
These settings can often be derived from the collection configuration in Cumulus as seen below:

```
{
  "States": {
    "CopyToArchive": {
      "Parameters": {
        "input.$": "$.payload",
        "config": {
          "providerId": "{$.meta.provider.id}",
          "executionId": "{$.cumulus_meta.execution_name}",
          "collectionShortname": "{$.meta.collection.name}",
          "collectionVersion": "{$.meta.collection.version}"
        },
        "optionalValues": {
          "config": {
            "excludedFileExtensions": "event.meta.collection.meta.orca.excludedFileExtensions",
            "s3MultipartChunksizeMb": "event.meta.collection.meta.s3MultipartChunksizeMb",
            "providerName": "event.meta.provider.name}",
            "defaultBucketOverride": "event.meta.collection.meta.orca.defaultBucketOverride",
            "defaultStorageClassOverride": "event.meta.collection.meta.orca.defaultStorageClassOverride"
          }
        }
      },
      "Type": "Task",
      "Resource": "${orca_lambda_copy_to_archive_arn}",
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
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive/schemas/config.json) for more information.

## Metadata SQS body configuration

The metadata SQS message body should contain the metadata attributes needed by Cumulus to perform analysis on discrepancies and for reconciliation.
These entries from the queue will then be ingested into a new ORCA lambda function that will update the records for the various objects in the ORCA catalog.
An example of a message is shown below:

```
{
      "provider": {"providerId": "1234", "name": "LPCUmumulus"},
      "collection": {
          "collectionId": "MOD14A1___061",
          "shortname": "MOD14A1",
          "version": "061",
      },
      "granule": {
          "cumulusGranuleId": "MOD14A1.061.A23V45.2020235",
          "cumulusCreateTime": "2020-01-01T23:00:00+00:00",
          "executionId": "f2fgh-356-789",
          "ingestTime": "2020-01-01T23:00:00Z",
          "lastUpdate": "2020-01-01T23:00:00Z",
          "files": [
              {
                  "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                  "cumulusArchiveLocation": "cumulus-archive",
                  "orcaArchiveLocation": "orca-archive",
                  "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                  "sizeInBytes": 100934568723,
                  "hash": "ACFH325128030192834127347",
                  "hashType": "SHA-256",
                  "storageClass": "GLACIER",
                  "version": "VXCDEG902",
                  "ingestTime": "2020-01-01T23:00:00Z",
                  "etag": "YXC432BGT789",
              }
          ],
      },
  }
```
Note that the `hash` and `hashType` are optional fields. See the SQS message schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_archive/schemas/body.json) for more information.

## pydoc copy_to_archive
[See the API documentation for more details.](API.md)