---
id: data-recovery
title: Data Recovery
description: Provides documentation for Operators to recover missing data.
---

An operator kicks off the recovery processes manually via the Cumulus Dashboard.
which then triggers an API that kicks off a recovery workflow. Recovery is an asynchronous operation since data
requested from GLACIER can take up to 4 hours or more to reconstitute
in most scenarios, and DEEP_ARCHIVE can take 12 hours. 
Since it is asynchronous, the recovery container
relies on a database to maintain the status of the request and event
driven triggers to restore the data once it has been reconstituted
from archive into an S3 bucket. Currently data is copied back to the
Cumulus S3 primary data bucket which is the default bucket. The operator has the option to override the default bucket with another restore bucket if desired. Determining
the status of the recovery job is done manually by querying the database
directly or by checking the status on the Cumulus Dashboard.

The following are the parameters needed for recovery workflow:

- buckets- AWS S3 bucket mapping used for Cumulus and ORCA configuration. Contains the following properties:
  - name (Required)- Name of the S3 bucket.
  - type (Optional)- the type of bucket - i.e. internal, public, private, protected. 

  It can be set up using the following configuration.
  ```json
        "config": {
          "buckets.$": "$.meta.buckets"
        }
    ```
    Example:

    ```json
    "buckets": {
            "protected": {"name": "sndbx-cumulus-protected", "type": "protected"},
            "internal": {"name": "sndbx-cumulus-internal", "type": "internal"},
            "private": {"name": "sndbx-cumulus-private", "type": "private"},
            "public": {"name": "sndbx-cumulus-public", "type": "public"}
        }
    ```
- fileBucketMaps- A list of dictionaries that contains details of the configured storage bucket and file regex. Contains the following properties:
  - regex (Required)- The regex that matches the file extension type.
  - bucket (Required))- The name of the key that points to the correct S3 bucket. Examples include public, private, protected, etc.
  - sampleFileName (Optional)- name of a sample file having extension.

  It can be set up using the following configuration.
  ```json
        "config": {
          "fileBucketMaps.$": "$.meta.collection.files"
        }
    ```
    Example: 
    ```json
        "fileBucketMaps":[
            {
            "regex":".*.h5$",
            "sampleFileName":"L0A_HR_RAW_product_0010-of-0420.h5",
            "bucket":"protected"
            },
            {
            "regex":".*.cmr.xml$",
            "sampleFileName":"L0A_HR_RAW_product_0010-of-0420.iso.xml",
            "bucket":"protected"
            }
    ```
- excludedFileExtensions (Optional)- A list of file extensions to ignore when copying files.
  It can be set up using the following configuration.
  ```json
        "config": {
          "excludedFileExtensions.$": "$.meta.collection.meta.orca.excludedFileExtensions"
        }
    ```
    Example: 
    ```json
        "excludedFileExtensions":[
            ".cmr",
            ".hdf
        ]
    ```
- defaultRecoveryTypeOverride (Optional)- Overrides the default restore type via a change in the collections configuration under `meta` tag as shown below. 
  ```json
  "meta": {
    "defaultRecoveryTypeOverride": "Standard"
  }
  ```
- defaultBucketOverride (Optional)- Overrides the default bucket to copy recovered files to.
  ```json
    "task_config": {
      "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"
    }
    ```
- s3MultipartChunksizeMb (Optional)- Overrides default_multipart_chunksize from TF. Defaults to 250.
  ```json
    "task_config": {
      "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}"
    }
    ```
- asyncOperationId (Optional)- The unique identifier used for tracking requests. If not present, it will be generated.
  ```json
    "task_config": {
      "asyncOperationId": "{$.cumulus_meta.asyncOperationId}"
    }
    ```

For full definition of the parameters, see the following schema.
- [request_from_archive schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_from_archive/schemas/config.json)
- [extract_filepath_from_granule schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/config.json)