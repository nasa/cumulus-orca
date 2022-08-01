---
id: research-deep-glacier-migration
title: Deep archive storage migration Research Notes
description: Research Notes on deep archive migration.
---
import MyImage from '@site/docs/templates/pan-zoom-image.mdx';
import useBaseUrl from '@docusaurus/useBaseUrl';

## Overview

The goal of this research is to provide an initial design and recommendation for migrating a customer's ORCA Flexible Retrieval (formerly Glacier) archive to DEEP ARCHIVE storage class. Deep archive S3 storage type is the cheapest glacier storage type currently present in AWS S3. For archive data that does not require immediate access such as backup or disaster recovery use cases, choosing `Deep Archive Access` tier could be a wise choice.
- Storage cost is ~$1/TB data per month. 
- Objects in the Deep Archive Access tier can be restored to the Frequent Access tier within 12-48 hours depending on the recovery type. Once the object is in the Frequent Access tier, users can send a GET request to retrieve the object. Like Flexible retrieval, the restored file is only available in frequent access for a configured number of days. For more information on retrieving objects from Flexible and Deep Archive storage, see the [documentation](See https://docs.amazonaws.cn/en_us/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html
).

### Assumptions

- List of objects already exists in orca catalog and S3 bucket.
- Users should be able to provide some information(possibly a collection or a combination of collection and granuleId) to retrieve objects possibly at the collection level.
- A serverless approach will be used utilizing several Python lambda functions, SNS/SQS and S3 bucket event notifications.
- The glacier bucket has versioning enabled.

### Use Cases

A user might want to 
- convert all the holdings or holdings with a known key prefix to DEEP ARCHIVE.
- convert specific collection or granules to DEEP ARCHIVE which might not have the same prefix.

### Implementation idea for migrating all ORCA holdings to deep archive.

This should be a manual step performed by the end user.

The steps for performing the migration are as follows:
1. Run the lifecycle configuration with transition_days = 0 as shown in the terraform code example below.
2. Wait 48 hours for all objects to migrate to deep archive.
3. There are two approaches to this
  - run a temporary lambda function that updates the catalog status table for storage class to deep archive.
  - (Recommended) Have a lifecycle rule applied to the glacier bucket that will trigger a lambda function for every `s3:LifecycleTransition` event in the bucket. This lambda will automatically update the ORCA catalog status table for storage class to deep archive.
4. Validate internal reconciliation for mismatches in storage class.
5. If no mismatch, disable/delete the lifecycle rules.

See architecture and workflow section below for details.


The following rule will move all objects with under prefix `tmp/` to DEEP ARCHIVE.

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
    filter {
      prefix = "tmp/"
    }
  }

```
:::tip
To migrate to a different storage class, change `storage_class` under transition block to the desired class in the terraform code above.
:::

### Implementation idea for migrating specific ORCA holdings to deep archive.

S3 lifecycle rule will not work in this case. 
Migration should be a two step process- first retrieve the objects and then copy the objects to deep archive.

1. User inputs a list of granuleId/collectionId or a combination of both via Cumulus console or API call.
2. This api should trigger a lambda function that queries the ORCA catalog and retrives the files via `Bulk Retrieval` and copies the objects to the glacier bucket as versioned object. Bulk retrievals are typically completed within 5–12 hours. The prices are lowest among all retrieval rates - $0.025 per 1,000 requests.
3. Once files are restored in the bucket, the bucket event notification for `ObjectRestore:Completed` action will trigger another lambda function that will copy the restored object to deep archive storage. In addition, this lambda should also notify end user on the copy progress as well as update the catalog status table for storage class. Services like SQS/SNS could be useful to track the migration progress. Note that the current existing restore workflow trigger should be disabled during the whole migration process to prevent triggering the `request_files` lambda and then re-enabled it migration is complete.
Another option here is to update existing recovery lambdas to perform the above tasks instead of creating new lambda. Additional research is needed to choose the right option.

See architecture and workflow section below for details.

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

Another option is to look into [S3 batch operations](https://docs.aws.amazon.com/AmazonS3/latest/userguide/batch-ops-initiate-restore-object.html). It can perform a single operation on lists of Amazon S3 objects and a single job can perform a specified operation on billions of objects containing exabytes of data.

The boto3 `copy_object` function can be used in the python lambda function as shown below. 

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

S3 batch operation can also be used in this case to perform the copying. For additional information, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/batch-ops-copy-object.html.


### Initial architecture design for migrating specific ORCA holdings to deep archive

The following is an initial workflow and architecture for ORCA deep archive migration for specific files. Note that this could possibly change during implementation phase.

<MyImage
    imageSource={useBaseUrl('img/Deep-Archive-Migration-workflow-specific-files.svg')}
    imageAlt="System Context"
    zoomInPic={useBaseUrl('img/zoom-in.png')}
    zoomOutPic={useBaseUrl('img/zoom-out.png')}
    resetPic={useBaseUrl('img/zoom-pan-reset.png')}
/>

<br />
<br />
<br />

<MyImage
    imageSource={useBaseUrl('img/ORCA-Deep-Archive-Migration-Architecture-specific-files.svg')}
    imageAlt="System Context"
    zoomInPic={useBaseUrl('img/zoom-in.png')}
    zoomOutPic={useBaseUrl('img/zoom-out.png')}
    resetPic={useBaseUrl('img/zoom-pan-reset.png')}
/>

<br />
<br />
<br />


### Initial architecture design for migrating all ORCA holdings to deep archive manually

The following is an initial workflow and architecture for ORCA deep archive migration for all files in the bucket. Note that this could possibly change during implementation phase.

<MyImage
    imageSource={useBaseUrl('img/Deep-Archive-Migration-workflow-manual.svg')}
    imageAlt="System Context"
    zoomInPic={useBaseUrl('img/zoom-in.png')}
    zoomOutPic={useBaseUrl('img/zoom-out.png')}
    resetPic={useBaseUrl('img/zoom-pan-reset.png')}
/>

<br />
<br />
<br />

<MyImage
    imageSource={useBaseUrl('img/ORCA-Deep-Archive-Migration-Architecture-manual.svg')}
    imageAlt="System Context"
    zoomInPic={useBaseUrl('img/zoom-in.png')}
    zoomOutPic={useBaseUrl('img/zoom-out.png')}
    resetPic={useBaseUrl('img/zoom-pan-reset.png')}
/>

<br />
<br />
<br />



### Cards created

- [Research task on S3 batch operations for copying objects](https://bugs.earthdata.nasa.gov/browse/ORCA-504)
- [Research how to notify end users on completion of specific object restore from glacier](https://bugs.earthdata.nasa.gov/browse/ORCA-499)
- [Implement lambda function for retrieving objects from glacier flexible retrieval](https://bugs.earthdata.nasa.gov/browse/ORCA-500)
- [Implement lambda function for copying existing S3 objects to DEEP ARCHIVE storage](https://bugs.earthdata.nasa.gov/browse/ORCA-501)
- [Update ORCA catalog records for files migrated to deep archive storage](https://bugs.earthdata.nasa.gov/browse/ORCA-503)


#### Sources
- https://pages.awscloud.com/Amazon-S3-Glacier-Deep-Archive-The-Cheapest-Storage-in-the-Cloud_2019_0409-STG_OD.html
- https://www.msp360.com/resources/blog/amazon-glacier-pricing-explained/
- https://stackoverflow.com/questions/61667968/moving-from-glacier-to-s3-glacier-deep-archive
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy_object
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html?highlight=delete#S3.Client.delete_object
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.restore_object
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html