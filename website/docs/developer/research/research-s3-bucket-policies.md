---
id: research-s3-bucket-best-practices
title: S3 Future Direction/Best Practices
description: Research notes on S3 best practices and some directions to take development.
---

## Overview

Presently, our S3 buckets are only defined through [documentation](../deployment-guide/creating-orca-glacier-bucket.md) and there are changes we wish to make to support future development.
This document aims to document the desired final state of our S3 buckets.

## Universal Suggestions

### Deny Public Access

For all buckets, make sure that [public access is disabled](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).
This is the default behavior for new buckets, but may not be enforced on pre-existing buckets.
Simply put, permissions should be granted on a case-by-case basis when needed.

### Deny Non-SSL Requests

There is a desire to disallow non-SSL requests. This can theoretically be done with the following untested statement:
```json
{
  "Sid": "AllowSSLRequestsOnly",
  "Action": "s3:*",
  "Effect": "Deny",
  "Resource": [
    "arn:aws:s3:::PREFIX-orca-bucket-name",
    "arn:aws:s3:::PREFIX-orca-bucket-name/*"
  ],
  "Condition": {
    "Bool": {
      "aws:SecureTransport": "false"
    }
  },
  "Principal": "*"
}
```

Testing should be done to identify any changes needed to lock out Non-SSL requests.
A [Jira task](https://bugs.earthdata.nasa.gov/browse/ORCA-452) has been created to implement this limit.

### Encryption

A [default encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html) should be used to encrypt data-at-rest, protecting it from attackers targeting storage mediums.
Since Orca S3 buckets presently reside in a different account from the producers/consumers, this presently requires a customer-managed key with [proper cross-account access](https://aws.amazon.com/premiumsupport/knowledge-center/s3-bucket-access-default-encryption/).
Note that objects already in an un-encrypted bucket will not be automatically encrypted if encryption is added.
A [Jira task](https://bugs.earthdata.nasa.gov/browse/ORCA-453) has been created to implement this feature.

## Versioned Glacier Bucket

Suggested name: PREFIX-orca-archive-versioned

Our [current Glacier bucket instructions](../deployment-guide/creating-orca-glacier-bucket.md) are well suited to storage.
There are a few changes we should consider.

Presently, ORCA does not handle versioned data, but it also does not preclude that capability in its buckets.
Setting versioning on Glacier allows for finer-grained data backup as users could recover from a specific version of a file being overwritten.
To enable development towards this goal, we should either replace the existing bucket with a versioned bucket and move existing data over, or instruct users on how to [enable versioning on their buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/manage-versioning-examples.html).

We should also remove the ACL capabilities due to AWS potential deprecation.
This will be detailed in a [future section](#acl-rule-replacement).

## WORM Glacier Bucket

Note that this work depends on completing (ORCA-351)[https://bugs.earthdata.nasa.gov/browse/ORCA-351]

Suggested name: PREFIX-orca-archive-worm

Some data will never have additional versions. This includes raw or near-raw satellite data. This data should be stored in a Read Once Write Many (WORM) model, and be protected from accidental deletion, as it is the foundation of all derived data.

Permissions for this bucket will likely be identical to the [Versioned Glacier Bucket](#versioned-glacier-bucket)

The naming dichotomy between this and the [Versioned Glacier Bucket](#versioned-glacier-bucket) is slightly deceptive, as this bucket will be versioned as well.
However, this is only to enable [Object Lock](https://aws.amazon.com/blogs/storage/protecting-data-with-amazon-s3-object-lock/)

There are two modes of Object Lock:
- Governance
  Users cannot delete files under this lock unless they both have an `s3:BypassGovernanceRetention` permission on the bucket, and they use an override when calling the delete endpoint.
  These holds automatically expire, but the expiration date can be arbitrarily far away.
- Compliance
  The lock must be removed before data can be deleted, and users must have special permissions to remove the lock.
  Locks have no expiration.

I recommend Governance mode so as to allow a global Object Lock policy; with Compliance, we would need to be able to remove the lock to delete files, so a global policy is not possible.
With a default policy of `Governance` mode and an arbitrarily long `Retention period`, data will be protected from accidental deletion by general users.

### Additional Considerations

Note that due to poor API returns, attempting to delete a file that cannot be deleted returns HTTP status code 204. When deletes are added to Orca, effort should be taken to return a proper error/success response to customers.

Due to technically being versioned, care should be taken when uploading as well.
Files should be rejected if they are already present in a WORM bucket, likely through an object lookup on the bucket.

There is still a race condition if two clients upload the same file simultaneously.
Checks should be done after a file is uploaded to make sure it is still the only version present.
If not, the uploaded version should be deleted, and an error message sent back to the client.
In the event that this mechanic fails, Internal Reconciliation should report errors on multiple versions of the same file within a WORM bucket.

## Reports Bucket

Suggested name: PREFIX-orca-reports

This bucket is relatively simple, as much of the interaction is automated through AWS. This bucket stores S3 Inventory reports generated by AWS, to be pulled in by `get_current_archive_list`.
Versioning is not used, and in general no changes are required beyond updating the Permissions to the policy below:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Cross Account Access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::012345678912:root"
      },
      "Action": [
        "s3:GetObject*",
        "s3:GetBucket*",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:PutBucketNotification"
      ],
      "Resource": [
        "arn:aws:s3:::PREFIX-orca-archive-versioned",
        "arn:aws:s3:::PREFIX-orca-archive-versioned/*"
      ]
    },
    {
      "Sid": "Inventory-PREFIX-orca-archive-versioned",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::PREFIX-orca-archive-versioned/*",
      "Condition": {
        "StringEquals": {
      	  "s3:x-amz-acl": "bucket-owner-full-control",
      	  "aws:SourceAccount": "0000000000000"
        },
      	"ArnLike": {
      	  "aws:SourceArn": "arn:aws:s3:::PREFIX-orca-archive-versioned"
      	}
      }
    },
    {
      "Sid": "Inventory-PREFIX-orca-archive-worm",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::PREFIX-orca-archive-worm/*",
      "Condition": {
        "StringEquals": {
      	  "s3:x-amz-acl": "bucket-owner-full-control",
      	  "aws:SourceAccount": "000000000000"
        },
      	"ArnLike": {
      	  "aws:SourceArn": "arn:aws:s3:::PREFIX-orca-archive-worm"
      	}
      }
    }
  ]
}
```
The Principal value is the AWS root user for your Cumulus application that will
access the ORCA archive bucket.

Replace the number in `arn:aws:iam::012345678912:root` with the value of your account number.

Replace the number `000000000000` with your DR account number.

The Resource value is the bucket and bucket paths that the Cumulus application
can access. Replace `PREFIX-orca-archive-versioned` with the name
of the Orca archive bucket created in the [Versioned Glacier Bucket](#versioned-glacier-bucket) section.

It may be possible to combine the two `Inventory-PREFIX-orca-archive-*` rules, but this has not yet been tested.

The [storage class](https://aws.amazon.com/s3/storage-classes/) should likely be modified to reduce costs associated with storing reports.
More research is needed, as the cost of downloading data goes up as the cost of storage goes down.

A lifecycle rule should be created to delete reports after a certain amount of time, tentatively placed at 30 days.
Instructions on creating this through TF can be found in the [official docs](https://registry.terraform.io/providers/hashicorp/aws/3.63.0/docs/resources/s3_bucket).
A Jira card for this [currently exists](https://bugs.earthdata.nasa.gov/browse/ORCA-451).

We should also remove the ACL capabilities due to AWS potential deprecation.
This will be detailed in a [future section](#acl-rule-replacement).

## Automation

It would be ideal to have a Terraform (TF) module that handles bucket creation/updates.
Unfortunately, since our deployment presently targets an account different from the Disaster Recovery account, this must be a separate TF deployment.
This will require the buckets to be recreated, so this will also require code to copy data from the old buckets to the new.
This will only need to be run once for switching from manual setup to TF setup, and will also help with cases where updates require buckets to be recreated.

A [Jira task](https://bugs.earthdata.nasa.gov/browse/ORCA-369) has been created to implement this feature.

## ACL Rule Replacement

Due to AWS suggesting that they will deprecate ACL rules, we should research a replacement for current ACL functionality.
Presently ACL is used primarily to allow ORCA full ownership over files uploaded to S3, via the addition of `"ACL": "bucket-owner-full-control"` when uploading via `copy_to_glacier`.
Buckets with ACL rules disabled default to objects being owned by the bucket, so this may be a clean switch.
Additional research and testing should be conducted.
A [Jira task](https://bugs.earthdata.nasa.gov/browse/ORCA-450) has been created to implement this switch.
