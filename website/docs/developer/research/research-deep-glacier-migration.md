---
id: research-deep-glacier-migration
title: Deep archive glacier migration Research Notes
description: Research Notes on dee parchive migration.
---

## Overview

Deep archive S3 storage type is the cheapest glacier storage type currently present in AWS S3. For archive data that does not require immediate access such as backup or disaster recovery use cases, choosing Deep Archive Access tier could be a wise choice.
- Storage cost is ~$1/TB data per month. 
- Objects in the Deep Archive Access tier are moved to the Frequent Access tier within 12 hours. Once the object is in the Frequent Access tier, users can send a GET request to retrieve the object.



### Initial Implementation Idea

- Retrieve all objects currently stored with Glacier Flexible Retrieval type using `Bulk Retrievel` which is the cheapest retrieval option. Bulk retrievals are typically completed within 5–12 hours. The prices are lowest among all retrieval rates - $0.0025 per GB plus $0.025 per 1,000 requests.
One option of bulk retrieval is to use python boto3 client for S3:

- using boto3 S3 client
```python
import boto3

s3 = boto3.client('s3')
for key in s3.list_objects(Bucket='orca-rhassan-sandbox-glacier')['Contents']:
    key_name = key['Key']
    try:
        response = s3.restore_object(
                Bucket='orca-rhassan-sandbox-glacier',
                Key = key_name,
                RestoreRequest={
                    'Days': 1,
                    'GlacierJobParameters': {
                        'Tier': 'Bulk',
                    },
                },
            )
        print(response)
    except Exception as ex:
        print(f"{ex} for {key_name}")

```
Also see existing ORCA [restore_object function](https://github.com/nasa/cumulus-orca/blob/develop/tasks/request_files/request_files.py#L548)


- Once all objects are retrieved, the bucket's lifecycle policy can be configured with `Deep Archive` storage type. 

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

- Another different implementation plan is to use [Amazon S3 Glacier Re:Freezer](https://aws.amazon.com/about-aws/whats-new/2021/04/new-aws-solutions-implementation-amazon-s3-glacier-re-freezer/)

It is a serverless solution that automatically copies all glacier archives to S3 bucket and S3 storage class. Most of the sample codes and architecture design is provided by AWS on github [here](https://github.com/awslabs/amazon-s3-glacier-refreezer). However, the technologies used include lambda, SQS, SNS, AWS Glue, Athena, step functions which could be complex.

### Future Direction
Based on initial research, it seems first retrieving all objects using bulk retrieval and then setting a lifecycle rule for transitioning to deep archive storage is the easiest and cheapest solution.

#### Sources
- https://pages.awscloud.com/Amazon-S3-Glacier-Deep-Archive-The-Cheapest-Storage-in-the-Cloud_2019_0409-STG_OD.html
- https://www.msp360.com/resources/blog/amazon-glacier-pricing-explained/
- https://stackoverflow.com/questions/61667968/moving-from-glacier-to-s3-glacier-deep-archive