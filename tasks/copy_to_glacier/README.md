[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_glacier/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_glacier/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The `copy_to_glacier` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier ORCA S3 bucket.


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

The `copy_to_glacier` lambda function can be deployed using terraform using the example shown in  `modules/lambdas/main.tf` file.

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
See the schema [input file](https://github.com/nasa/cumulus-orca/blob/develop/tasks/copy_to_glacier/schemas/input.json) for more information.


## Output

The `copy_to_glacier` lambda will, as the name suggests, copy a file from its current source destination. The destination location is defined as 
`${glacier_bucket}/${filepath}`, where `${glacier_bucket}` is pulled from the environment variable `ORCA_DEFAULT_BUCKET` and `${filepath}` is pulled from the Cumulus granule object input.

The output of this lambda is a dictionary with a `granules` and `copied_to_glacier` attributes.  See the schema [output file](https://github.com/nasa/cumulus-orca/blob/develop/tasks/copy_to_glacier/schemas/output.json) for more information. Below is an example of the output:

```json
{
	"granules": [
    {
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "dataType": "MOD09GQ",
      "version": "006",
      "files": [
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318361000,
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

To configure a collection to enable ORCA, add the line `granuleRecoveryWorkflow: OrcaRecoveryWorkflow` to the collection configuration. It is also possible to exclude copying certain types of files to glacier bucket by adding the file type values to an `excludeFileTypes` variable.  An example of a collection configuration is given below:

```
{
  "queriedAt": "2019-11-07T22:49:46.842Z",
  "name": "L0A_HR_RAW",
  "version": "1",
  "sampleFileName": "L0A_HR_RAW_product_0001-of-0420.h5",
  "dataType": "L0A_HR_RAW",
  "granuleIdExtraction": "^(.*)((\\.cmr\\.json)|(\\.iso\\.xml)|(\\.tar\\.gz)|(\\.h5)|(\\.h5\\.mp))$",
  "reportToEms": true,
  "granuleId": "^.*$",
  "provider_path": "L0A_HR_RAW/",
  "meta": {
    "granuleRecoveryWorkflow": "OrcaRecoveryWorkflow",
    "excludeFileTypes": [".cmr", ".xml", ".met"]
  }
}
```
See the schema [configuration file](https://github.com/nasa/cumulus-orca/blob/develop/tasks/copy_to_glacier/schemas/config.json) for more information.

## pydoc copy_to_glacier

```
Help on module copy_to_glacier:

NAME
    copy_to_glacier

FUNCTIONS
    copy_granule_between_buckets(source_bucket_name: str, source_key: str, destination_bucket: str, destination_key: str, multipart_chunksize_mb: int) -> None
        Copies granule from source bucket to destination.
        Args:
            source_bucket_name: The name of the bucket in which the granule is currently located.
            source_key: source Granule path excluding s3://[bucket]/
            destination_bucket: The name of the bucket the granule is to be copied to.
            destination_key: Destination granule path excluding s3://[bucket]/
            multipart_chunksize_mb: The maximum size of chunks to use when copying.
        Returns:
            None
    
    handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any
        Lambda handler. Runs a cumulus task that
        Copies the files in {event}['input'] from the collection specified in
        {config} to the default ORCA bucket. Environment variables must be set to
        provide a default ORCA bucket to store the files in.
            Environment Vars:
                ORCA_DEFAULT_BUCKET (str, required): Name of the default S3 Glacier
                                                     ORCA bucket files should be
                                                     archived to.
                DEFAULT_MULTIPART_CHUNKSIZE_MB (int, required): The default maximum size of chunks to use when copying.
                                                                     Can be overridden by collection config.
        
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
        Copies the files in {event}['input'] from the collection specified in {config}
        to the ORCA glacier bucket defined in ORCA_DEFAULT_BUCKET.
        
            Environment Variables:
                ORCA_DEFAULT_BUCKET (string, required): Name of the default ORCA S3 Glacier bucket.
                DEFAULT_MULTIPART_CHUNKSIZE_MB (int, optional): The default maximum size of chunks to use when copying. Can be overridden by collection config.
        
        Args:
            event: Passed through from {handler}
            context: An object required by AWS Lambda. Unused.
        
        Returns:
            A dict representing input and copied files. See schemas/output.json for more information.

DATA
    Any = typing.Any
    COLLECTION_META_KEY = 'meta'
    CONFIG_COLLECTION_KEY = 'collection'
    CONFIG_MULTIPART_CHUNKSIZE_MB_KEY = 'multipart_chunksize_mb'
    Dict = typing.Dict
    EXCLUDE_FILE_TYPES_KEY = 'excludeFileTypes'
    List = typing.List
    MB = 1048576
    Union = typing.Union
```

