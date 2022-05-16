---
id: research-multipart-chunksize
title: Multipart Chunksize Research Notes
description: Research Notes on Modifying Multipart-Chunksize for copy_to_glacier.
---

## Overview

[copy_to_glacier](https://github.com/nasa/cumulus-orca/blob/2f2600a2edd85e0af216d78180c5d46ebda03060/tasks/copy_to_glacier/copy_to_glacier.py#L50)
uses a copy command that has a chunk-size for multi-part transfers.
We currently are using the default value of 8mb, which will cause problems when transferring large files, sometimes exceeding 120Gb.

### Implementation Details
- [Docs for the copy command](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy) mention a `Config` parameter of type `TransferConfig`.
- [Docs for TransferConfig](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/customizations/s3.html#boto3.s3.transfer.TransferConfig) state that it has a property
- Given the above, we can modify the `s3.copy` command to
  ```python
  s3.copy(
    copy_source,
    destination_bucket, destination_key,
    ExtraArgs={
        'StorageClass': 'GLACIER',
        'MetadataDirective': 'COPY',
        'ContentType': s3.head_object(Bucket=source_bucket_name, Key=source_key)['ContentType'],
        'ACL': 'bucket-owner-full-control'  # Sets the x-amz-acl URI Request Parameter. Needed for cross-OU copies.
    },
    Config=TransferConfig(multipart_chunksize=multipart_chunksize_mb * MB)
  )
  ```
- This will require a variable passed into the lambda.
  - Could be set at the collection level under `config['collection']['s3MultipartChunksizeMb']` with a default value in the lambdas/main.tf entry for `copy_to_glacier` defined as
    ```
    environment {
      variables = {
        ORCA_DEFAULT_BUCKET = var.orca_default_bucket,
        DEFAULT_ORCA_COPY_CHUNK_SIZE_MB = var.orca_copy_chunk_size
      }
    }
    ```
  - Could also be an overall environment variable, though this is less flexible. In the lambdas/main.tf entry for `copy_to_glacier` this would look like
    ```
    environment {
      variables = {
        ORCA_DEFAULT_BUCKET = var.orca_default_bucket,
        ORCA_COPY_CHUNK_SIZE_MB = var.orca_copy_chunk_size
      }
    }
    ```
- The above should be added to other TF files such as terraform.tfvars, orca/main.tf, orca/variables.tf, and lambdas/variables.tf as well as documentation.

### Future Direction
- Recommend adding the environment variable `ORCA_COPY_CHUNK_SIZE_MB` to TF and Lambda.
  - Worth waiting to use the same name as Cumulus, as they are going through a similar change.
- I have read in a couple of sources that increasing `io_chunksize` can also have a significant impact on performance. May be worth looking into if more improvements are desired.
  - The other variables should be considered as well.
