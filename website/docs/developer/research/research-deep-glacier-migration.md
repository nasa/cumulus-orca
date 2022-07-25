---
id: research-deep-glacier-migration
title: Deep archive storage migration Research Notes
description: Research Notes on deep archive migration.
---

## Overview

Deep archive S3 storage type is the cheapest glacier storage type currently present in AWS S3. For archive data that does not require immediate access such as backup or disaster recovery use cases, choosing `Deep Archive Access` tier could be a wise choice.
- Storage cost is ~$1/TB data per month. 
- Objects in the Deep Archive Access tier can be moved to the Frequent Access tier within 12 hours. Once the object is in the Frequent Access tier, users can send a GET request to retrieve the object.


### Assumptions

- List of objects already exists in orca catalog and S3 bucket.
- Users should be able to provide some information(filename) to retrieve objects possibly at the collection level.

### Initial Implementation Idea

Migration should be a 2 step process- first retrieve the objects and then copy the objects to deep archive.

- Retrieve all objects currently stored with Glacier Flexible Retrieval type using `Bulk Retrieval` which is the cheapest retrieval option. Bulk retrievals are typically completed within 5–12 hours. The prices are lowest among all retrieval rates - $0.0025 per GB plus $0.025 per 1,000 requests.
One option of bulk retrieval is to use python boto3 client for S3:

```python
import boto3

#this objects list should be provided by the user
retrieve_objects = ['test1.xml', 'test2.xml']

s3 = boto3.client('s3')
for retrieve_object in retrieve_objects:
    try:
        response = s3.restore_object(
                Bucket='orca-rhassan-sandbox-glacier', # bucket that contains the objects currently in glacier flexible retrieval
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
Output:
```
{'ResponseMetadata': {'RequestId': '61ZWC27NHSFNMYJT', 'HostId': 'ItKZaYvn9rfi6ZVYmUjfZX24mKJlDZlciT9MaKK0aHiNuLWB3Pt8WSEMNt5yBK+5u+MJfzjFDfU=', 'HTTPStatusCode': 202, 'HTTPHeaders': {'x-amz-id-2': 'ItKZaYvn9rfi6ZVYmUjfZX24mKJlDZlciT9MaKK0aHiNuLWB3Pt8WSEMNt5yBK+5u+MJfzjFDfU=', 'x-amz-request-id': '61ZWC27NHSFNMYJT', 'date': 'Sun, 24 Jul 2022 18:01:33 GMT', 'server': 'AmazonS3', 'content-length': '0'}, 'RetryAttempts': 0}}
{'ResponseMetadata': {'RequestId': 'PNN4XXA5SYTBBRKG', 'HostId': 'HgiIiqfb0hZPHgZml98VCyLLfD5LyQ8pSLpgGN6hwUUMtmcPZoo/ACbCL1rXz+pXZ4Ce2UEe34s=', 'HTTPStatusCode': 202, 'HTTPHeaders': {'x-amz-id-2': 'HgiIiqfb0hZPHgZml98VCyLLfD5LyQ8pSLpgGN6hwUUMtmcPZoo/ACbCL1rXz+pXZ4Ce2UEe34s=', 'x-amz-request-id': 'PNN4XXA5SYTBBRKG', 'date': 'Sun, 24 Jul 2022 18:01:34 GMT', 'server': 'AmazonS3', 'content-length': '0'}, 'RetryAttempts': 0}}
```

Also see existing ORCA [restore_object function](https://github.com/nasa/cumulus-orca/blob/develop/tasks/request_files/request_files.py#L548)
Make sure the S3 bucket policy has permission for `s3:PutObject*` action otherwise user will see access denied error. See this [policy](https://github.com/nasa/cumulus-orca/blob/develop/website/docs/developer/deployment-guide/creating-orca-glacier-bucket.md#archive-bucket) for additional details.

Once all files are restored from glacier, there should be some mechanism that will notify users that the retrieval process is complete. One approach could be to enable event notifications in bucket that will trigger either an SQS, SNS or lambda. This will require additional research since AWS notifies for each `s3:ObjectRestore:Completed` API call and not for a specific number of objects.

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
:::warning
This will not work in case a user only wants to migrate some specific objects to deep archive.
:::

- If a user only wants to restore some specific objects instead of all objects in the bucket, we can use a lambda function or a script that will run after 12 hours and copy the restored objects to deep archive S3 storage using boto3 `copy_object` function as shown below. 

:::important
Note that there should be some confirmation that all requested objects are successfully restored before running this script.
:::

```python
import boto3

s3 = boto3.client('s3')
#this list should be provided by the user
retrieve_objects = ['test1.xml', 'test2.xml']
bucket_name = 'orca-rhassan-sandbox-glacier'
for migrate_object in retrieve_objects:
    try:
        response = s3.copy_object(
            Bucket= bucket_name,  #bucket name where the object is stored currently
            CopySource={'Bucket': bucket_name, 'Key': migrate_object},
            Key = migrate_object, #keyname of object after migration
            StorageClass='DEEP_ARCHIVE'
        )
        print(response)
        print(f"copy succeeded for object {migrate_object} having E tag " + response["CopyObjectResult"]["ETag"])
    except Exception as ex:
        print(ex)
```
Output:
```
{'ResponseMetadata': {'RequestId': 'EM3XDZ6BB7FJJ88W', 'HostId': '/HayQvl8E2cCsclvO0b4MQUHAJnf7exmJhCILDsXfCieuaJIrAt5ZD9ocOkaam6rQbgXt0qx18A=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '/HayQvl8E2cCsclvO0b4MQUHAJnf7exmJhCILDsXfCieuaJIrAt5ZD9ocOkaam6rQbgXt0qx18A=', 'x-amz-request-id': 'EM3XDZ6BB7FJJ88W', 'date': 'Sun, 24 Jul 2022 18:13:32 GMT', 'x-amz-storage-class': 'DEEP_ARCHIVE', 'content-type': 'application/xml', 'server': 'AmazonS3', 'content-length': '234'}, 'RetryAttempts': 0}, 'CopyObjectResult': {'ETag': '"66d8119b127d165f8bc66fa66e0e35a6"', 'LastModified': datetime.datetime(2022, 7, 24, 18, 13, 32, tzinfo=tzutc())}}
copy succeeded for object test1.xml having E tag "66d8119b127d165f8bc66fa66e0e35a6"
{'ResponseMetadata': {'RequestId': 'SA312G5B2RRN5P0C', 'HostId': '/YIl4aUR+CAov4/pxzzd8oVORmYYsewTbwZfnVDkWRa+8g/epeQ7KEZGqSVgcx5LheMhU/dXMfw=', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amz-id-2': '/YIl4aUR+CAov4/pxzzd8oVORmYYsewTbwZfnVDkWRa+8g/epeQ7KEZGqSVgcx5LheMhU/dXMfw=', 'x-amz-request-id': 'SA312G5B2RRN5P0C', 'date': 'Sun, 24 Jul 2022 18:13:33 GMT', 'x-amz-storage-class': 'DEEP_ARCHIVE', 'content-type': 'application/xml', 'server': 'AmazonS3', 'content-length': '234'}, 'RetryAttempts': 0}, 'CopyObjectResult': {'ETag': '"14694ab9e3089a7c29e0dc9add4a82ab"', 'LastModified': datetime.datetime(2022, 7, 24, 18, 13, 33, tzinfo=tzutc())}}
copy succeeded for object test2.xml having E tag "14694ab9e3089a7c29e0dc9add4a82ab"
```
- Once objects are copied successfully, the old objects in standard storage can be deleted using boto3 client `delete_object` API call per object or `delete_objects` which can delete upto 1000 objects with a single API call.

```python
import boto3

s3 = boto3.client('s3')
#this list should be provided by the user
delete_objects = ['1.xml', '2.xml']
bucket_name = 'orca-rhassan-sandbox-glacier'
for delete_object in delete_objects:
    try:
        response = s3.delete_object(
            Bucket= bucket_name,  #bucket name where the object is stored currently
            Key=delete_object
        )
        print(response)
        print(f"{delete_object} deleted")
    except Exception as ex:
        print(ex)
```
Output:
```
{'ResponseMetadata': {'RequestId': 'C38C978YGKEF6BCR', 'HostId': 'iPQXFX3m215jhR0giFh/3cmbbuqIjQejXO8zQIxGjEnDbwoA1Yb+ZLvPDB2xJ5UmpEACMzAVD6c=', 'HTTPStatusCode': 204, 'HTTPHeaders': {'x-amz-id-2': 'iPQXFX3m215jhR0giFh/3cmbbuqIjQejXO8zQIxGjEnDbwoA1Yb+ZLvPDB2xJ5UmpEACMzAVD6c=', 'x-amz-request-id': 'C38C978YGKEF6BCR', 'date': 'Sun, 24 Jul 2022 18:29:20 GMT', 'server': 'AmazonS3'}, 'RetryAttempts': 0}} test1.xml deleted {'ResponseMetadata': {'RequestId': 'C38CPZ61SV9DH9A8', 'HostId': 'FOU0+D9gnBM7rwI4a7eO3ZXxmxfdcKxYWb7DtwnN4hx0fgHDfYE5W99vPZxqBNqJEFmPcbuoMXQ=', 'HTTPStatusCode': 204, 'HTTPHeaders': {'x-amz-id-2': 'FOU0+D9gnBM7rwI4a7eO3ZXxmxfdcKxYWb7DtwnN4hx0fgHDfYE5W99vPZxqBNqJEFmPcbuoMXQ=', 'x-amz-request-id': 'C38CPZ61SV9DH9A8', 'date': 'Sun, 24 Jul 2022 18:29:20 GMT', 'server': 'AmazonS3'}, 'RetryAttempts': 0}}
test2.xml deleted
```

### Cards created

- ORCA-499 -Research how to notify end users on completion of specific object restore from glacier.
- ORCA-500- Implement script for retrieving objects from glacier flexible retrieval.
- ORCA-501- Implement script/lambda function for copying existing S3 objects to DEEP ARCHIVE storage
- ORCA-502- Delete old objects that have been copied over to deep archive from S3.

#### Sources
- https://pages.awscloud.com/Amazon-S3-Glacier-Deep-Archive-The-Cheapest-Storage-in-the-Cloud_2019_0409-STG_OD.html
- https://www.msp360.com/resources/blog/amazon-glacier-pricing-explained/
- https://stackoverflow.com/questions/61667968/moving-from-glacier-to-s3-glacier-deep-archive
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html?highlight=delete#S3.Client.delete_object
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.restore_object