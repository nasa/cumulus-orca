---
id: research-deep-glacier-migration
title: Deep archive glacier migration Research Notes
description: Research Notes on dee parchive migration.
---

## Overview

Deep archive S3 storage type is the cheapest glacier storage type currently present in AWS S3. For archive data that does not require immediate access such as backup or disaster recovery use cases, choosing Deep Archive Access tier could be a wise choice.
- Storage cost is ~$1/TB data per month. 
- Objects in the Deep Archive Access tier are moved to the Frequent Access tier within 12 hours. Once the object is in the Frequent Access tier, users can send a GET request to retrieve the object.


### Assumptions

- List of objects already exist in orca catalog and S3 bucket.
- Users should be able to provide some information(filename) to retrieve objects- possibly at the collection level.

### Initial Implementation Idea

- Retrieve all objects currently stored with Glacier Flexible Retrieval type using `Bulk Retrievel` which is the cheapest retrieval option. Bulk retrievals are typically completed within 5–12 hours. The prices are lowest among all retrieval rates - $0.0025 per GB plus $0.025 per 1,000 requests.
One option of bulk retrieval is to use python boto3 client for S3:

- using boto3 S3 client
```python
import boto3

#this objects list will be provided by the user
retrieve_objects = []

s3 = boto3.client('s3')
for retrieve_object in retrieve_objects:
    try:
        response = s3.restore_object(
                Bucket='orca-rhassan-sandbox-glacier',
                Key = retrieve_object,
                RestoreRequest={
                    'Days': 30,
                    'GlacierJobParameters': {
                        'Tier': 'Bulk',
                    },
                },
            )
        print(response)
    except Exception as ex:
        print(f"{ex} for {retrieve_object}")

```
Also see existing ORCA [restore_object function](https://github.com/nasa/cumulus-orca/blob/develop/tasks/request_files/request_files.py#L548)

Once all files are restored from glacier, there should be some mechanism that will notify users that the retrieval process is complete. One approach could be to enable event notifications in bucket that will trigger either an SQS, SNS or lambda. This will require additional research since AWS notifies for each `s3:ObjectRestore:Completed` API call.

- Once all objects are retrieved in standard S3 storage, the bucket's lifecycle policy can be configured with `Deep Archive` storage type if the whole bucket objects have to be moved to deep archive.

```teraform
resource "aws_s3_bucket_lifecycle_configuration" "bucket-config" {
  bucket = aws_s3_bucket.bucket.bucket

  rule {
    id = "transition to deep archive"
    status = "Enabled"

    transition {
      days          = 0
      storage_class = "DEEP_ARCHIVE"
    }
  }

```
:::note
This will not work in case a user only wants to migrate some specific objects to deep archive.
:::

- If a user only wants to restore some specific objects instead of all objects in the bucket, we can use a lambda function or a script that will copy the restored objects to deep archive S3 storage using boto3 `copy_object` function as shown below.

```python
import boto3

#this list should be provided by the user
retrieve_objects = []

for migrate_object in retrieve_objects:
    try:
        response = s3.copy_object(
            Bucket='rhassan-deeparchive-test',
            CopySource={'Bucket': 'rhassan-deeparchive-test', 'Key': migrate_object},
            Key = migrate_object,
            StorageClass='DEEP_ARCHIVE'
        )
        print(response)
        print(f"copy succeeded for object {migrate_object} having E tag " + response["CopyObjectResult"]["ETag"])
    except Exception as ex:
        print(ex)
```

### Future Direction
Based on initial research, first retrieving all objects using bulk retrieval and then running the lambda or migration script to copy retrieved objects to deep archive seem to a reasonable direction to go.

### Cards created

- ORCA-499 -Research how to notify end users on completion of specific object restore from glacier.

#### Sources
- https://pages.awscloud.com/Amazon-S3-Glacier-Deep-Archive-The-Cheapest-Storage-in-the-Cloud_2019_0409-STG_OD.html
- https://www.msp360.com/resources/blog/amazon-glacier-pricing-explained/
- https://stackoverflow.com/questions/61667968/moving-from-glacier-to-s3-glacier-deep-archive
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object