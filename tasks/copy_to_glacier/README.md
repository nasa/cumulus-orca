[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_glacier/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_glacier/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The `copy_to_glacier` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier ORCA S3 bucket. It also sends additional metadata attributes to metadata SQS queue needed for Cumulus reconciliation.


## Exclude files by extension.

You are able to specify a list of file types (extensions) that you'd like to exclude from the backup/copy_to_glacier functionality. This is done on a per-collection basis, configured in the `meta` variable of a Cumulus collection configuration:

```json
{
  ...
  "meta": {
    "excludeFileTypes": [".cmr", ".xml", ".cmr.xml"]
  }
}
```

Note that this must be done for _each_ collection configured. If this list is empty or not included in the meta configuration, the `copy_to_glacier` function will include files with all extensions in the backup.


## Build

To build the **copy_to_glacier** lambda, run the `bin/build.sh` script from the
`tasks/copy_to_glacier` directory in a docker
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
bash-4.2# cd tasks/copy_to_glacier/

# Run the tests
bash-4.2# bin/build.sh
```

### Testing copy_to_glacier

To run unit tests for **copy_to_glacier**, run the `bin/run_tests.sh` script from the
`tasks/copy_to_glacier` directory. Ideally, the tests should be run in a docker
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
bash-4.2# cd tasks/copy_to_glacier/

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.

## Deployment

The `copy_to_glacier` lambda function can be deployed using terraform using the example shown in  `"aws_lambda_function" "copy_to_glacier"` resource block of `modules/lambdas/main.tf` file.

## Input

The `handler` function `handler(event, context)` expects input as a Cumulus Message. Event is passed from the AWS step function workflow. The actual format of that input may change over time, so we use the [cumulus-message-adapter](https://github.com/nasa/cumulus-message-adapter) package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

The `copy_to_glacier` lambda function expects that the input payload has a `granules` object, similar to the output of `MoveGranulesStep`:

```json
{
  "payload": {
    "granules": [
      {
        "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
        "dataType": "MOD09GQ",
        "version": "006",
        "createdAt": "2021-10-08T19:24:07.605323Z",
        "files": [
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318361000,
            "bucket": "orca-sandbox-protected",
            "url_path": "MOD09GQ/006/",
            "type": "",
            "filename": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318366000,
            "bucket": "orca-sandbox-private",
            "url_path": "MOD09GQ/006",
            "type": "",
            "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318372000,
            "bucket": "orca-sandbox-public",
            "url_path": "MOD09GQ/006",
            "type": "",
            "filename": "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "bucket": "orca-sandbox-private",
            "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "type": "metadata",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "url_path": "MOD09GQ/006"
          }
        ],
        "sync_granule_duration": 1728
      }
    ]
  }
}
```
From the json file, the `filepath` shows the current S3 location of files that need to be copied over to glacier ORCA S3 bucket such as `"filename": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf"`.
**Note:** We suggest that the `copy_to_glacier` task be placed any time after the `MoveGranulesStep`. It will propagate the input `granules` object as output, so it can be used as the last task in the workflow.
See the schema [input file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/input.json) for more information.


## Output

The `copy_to_glacier` lambda will, as the name suggests, copy a file from its current source destination. The destination location is defined as 
`${glacier_bucket}/${filepath}`, where `${glacier_bucket}` is pulled from the environment variable `ORCA_DEFAULT_BUCKET` and `${filepath}` is pulled from the Cumulus granule object input.

The output of this lambda is a dictionary with a `granules` and `copied_to_glacier` attributes.  See the schema [output file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/output.json) for more information. Below is an example of the output:

```json
{
	"granules": [
    {
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "dataType": "MOD09GQ",
      "version": "006",
      "createdAt": "2021-10-08T19:24:07.605323Z",
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
	"copied_to_glacier": [
      "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
      "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml"
  ]
}
```

## Configuration

As part of the [Cumulus Message Adapter configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration) 
for `copy_to_glacier`, the `excludeFileTypes`, `multipart_chunksize_mb`, `providerId`, `executionId`, `collection_shortname` and `collection_version` keys must be present under the 
`task_config` object as seen below. Per the [config schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/config.json), 
the values of the keys are used the following ways. The `provider` key should contain an `id` key that returns the provider id from Cumulus. The `cumulus_meta` key should contain an `execution_name` key that returns the step function execution ID from AWS. 
The `collection` key value should contain a `name` key and a `version` key that return the required collection shortname and collection version from Cumulus respectively.
The `collection` key value should also contain a meta object with an optional `excludeFileTypes` key that is used to determine file patterns that should not be 
sent to ORCA. The optional `multipart_chunksize_mb` is used to override the default setting for the lambda 
s3 copy maximum multipart chunk size value when copying large files to ORCA. Both of these settings can 
often be derived from the collection configuration in Cumulus as seen below:

```
{
  "States": {
    "CopyToGlacier": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "task_config": {
            "multipart_chunksize_mb": "{$.meta.collection.multipart_chunksize_mb"},
            "excludeFileTypes": "{$.meta.collection.meta.excludeFileTypes}",
            "providerId": "{$.meta.provider.id}",
            "executionId": "{$.cumulus_meta.execution_name}",
            "collection_shortname": "{$.meta.collection.name}",
            "collection_version": "{$.meta.collection.version}"
          }
        }
      },
      "Type": "Task",
      "Resource": "${orca_lambda_copy_to_glacier_arn}",
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
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/config.json) for more information.

## Metadata SQS body configuration

The metadata SQS message body should contain the metadata attributes needed by Cumulus to perform analysis on discrepencies and for reconciliation.
These information from the queue will then be ingested into a new ORCA lambda function that will update the records for the various objects in the ORCA catalog.
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
          "cumulusCreateTime": "2020-01-01T23:00:00Z",
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
                  "version": "VXCDEG902",
                  "ingestTime": "2020-01-01T23:00:00Z",
                  "etag": "YXC432BGT789",
              }
          ],
      },
  }
```
Note that the `hash` and `hashType` are optional fields. See the SQS message schema [configuration file](https://github.com/nasa/cumulus-orca/blob/master/tasks/copy_to_glacier/schemas/body.json) for more information.

## pydoc copy_to_glacier

```
Help on module copy_to_glacier:

NAME
    copy_to_glacier

FUNCTIONS
    copy_granule_between_buckets(source_bucket_name: str, source_key: str, destination_bucket: str, destination_key: str, multipart_chunksize_mb: int) -> None
        Copies granule from source bucket to destination. Also queries the destination_bucket to get additional metadata file info.
        Args:
            source_bucket_name: The name of the bucket in which the granule is currently located.
            source_key: source Granule path excluding s3://[bucket]/
            destination_bucket: The name of the bucket the granule is to be copied to.
            destination_key: Destination granule path excluding s3://[bucket]/
            multipart_chunksize_mb: The maximum size of chunks to use when copying.
        Returns:
           A dictionary containing all the file metadata needed for reconciliation with Cumulus with the following keys:
                  "cumulusArchiveLocation" (str): Cumulus S3 bucket where the file is stored in.
                  "orcaArchiveLocation" (str): ORCA S3 Glacier bucket that the file object is stored in
                  "keyPath" (str): Full AWS key path including file name of the file where the file resides in ORCA.
                  "sizeInBytes" (str): Size of the object in bytes
                  "version" (str): Latest version of the file in the S3 Glacier bucket
                  "ingestTime" (str): Date and time the file was originally ingested into ORCA.
                  "etag" (str): etag of the file object in the AWS S3 Glacier bucket.
        
    handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any
        Lambda handler. Runs a cumulus task that
        Copies the files in {event}['input']
        to the default ORCA bucket. Environment variables must be set to
        provide a default ORCA bucket to store the files in.
            Environment Vars:
                ORCA_DEFAULT_BUCKET (str, required): Name of the default S3 Glacier
                                                     ORCA bucket files should be
                                                     archived to.
                DEFAULT_MULTIPART_CHUNKSIZE_MB (int, required): The default maximum size of chunks to use when copying.
                                                                     Can be overridden by collection config.
                METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.
        
        Args:
            event: Event passed into the step from the AWS step function workflow.
                See schemas/input.json and schemas/config.json for more information.
        
        
            context: An object required by AWS Lambda. Unused.
        
        Returns:
            The result of the cumulus task. See schemas/output.json for more information.
    
    should_exclude_files_type(granule_url: str, exclude_file_types: List[str]) -> bool
        Tests whether or not file is included in {excludeFileTypes} from copy to glacier.
        Args:
            granule_url: s3 url of granule.
            exclude_file_types: List of extensions to exclude in the backup
        Returns:
            True if file should be excluded from copy, False otherwise.
    
    task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]
        Copies the files in {event}['input']
        to the ORCA glacier bucket defined in ORCA_DEFAULT_BUCKET.
        
            Environment Variables:
                ORCA_DEFAULT_BUCKET (string, required): Name of the default ORCA S3 Glacier bucket.
                DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional): The default maximum size of chunks to use when copying. Can be overridden by collection config.
                METADATA_DB_QUEUE_URL (string, required): SQS URL of the metadata queue.
        
        Args:
            event: Passed through from {handler}
            context: An object required by AWS Lambda. Unused.
        
        Returns:
            A dict representing input and copied files. See schemas/output.json for more information.
DATA
    Any = typing.Any
    CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = 'multipart_chunksize_mb'
    Dict = typing.Dict
    CONFIG_EXCLUDE_FILE_TYPES_KEY = 'excludeFileTypes'
    List = typing.List
    MB = 1048576
    Union = typing.Union
```

## pydoc sqs_library.py

```
Help on sqs_library:

NAME
    sqs_library

FUNCTIONS
    post_to_metadata_queue(sqs_body: Dict[str, Any], metadata_queue_url: str,) -> None:
        Posts metadata information to the metadata SQS queue.
        Args:
            sqs_body: A dictionary containing the metadata objects that will be sent to SQS.
            metadata_queue_url: The metadata SQS queue URL defined by AWS.
        Returns:
            None
    get_aws_region() -> str:
        Gets AWS region variable from the runtime environment variable.
        Args:
            None
        Returns:
            The AWS region variable.
        Raises:
            Exception: Thrown if AWS region is empty or None.
    
    retry_error(max_retries: int, backoff_in_seconds: int, backoff_factor: int) -> Callable[[Callable[[], RT]], Callable[[], RT]]:
        Decorator takes arguments to adjust number of retries and backoff strategy.
        Args:
            max_retries (int): number of times to retry in case of failure.
            backoff_in_seconds (int): Number of seconds to sleep the first time through.
            backoff_factor (int): Value of the factor used for backoff.
DATA
    Any = typing.Any
    Callable = typing.Callable
    Dict = typing.Dict
    TypeVar = typing.TypeVar
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2
    INITIAL_BACKOFF_IN_SECONDS = 1
```






    