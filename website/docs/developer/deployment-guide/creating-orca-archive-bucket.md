---
id: deployment-s3-bucket
title: Creating the Archive Bucket
description: Provides developer with information on archive storage solutions.
---

ORCA maintains a cloud ready backup of science and ancillary data 
in one of various [storage classes](../../operator/storage-classes.md) 
in [S3](https://aws.amazon.com/s3/)
for the long term. The ORCA archive bucket can live in any NGAP Organizational
Unit (OU).

:::important Archive Bucket OU Placement

Best practice is to place the ORCA archive bucket in your Disaster Recovery OU.
This is done to better separate the costs associated with the cloud ready backup
from primary Cumulus holdings and ingest and archive activity. See the
[ORCA Architecture Introduction documentation](../../about/architecture/architecture-intro.mdx)
for more information.

:::

The sections below go into further detail on creating the ORCA archive bucket.

## Create the ORCA Archive and Report Buckets

Prior to creating the S3 buckets, make sure the deployment environment is created
per the [Creating the Deployment Environment](setting-up-deployment-environment.mdx)
documentation.

To create the ORCA buckets run the AWS CLI command below twice, once for your archive bucket and once for your report bucket.
Replace the \[place holder text\] with proper values for your deployment.

```bash
aws s3api create-bucket \
    --bucket [orca bucket name] \
    --profile [AWS OU profile]  \
    --region us-west-2 \
    --create-bucket-configuration "LocationConstraint=us-west-2"
```

- **\[AWS OU profile\]** - This is the AWS profile name to use to connect to the proper OU where the bucket will be created.
- **\[orca bucket name\]** - This is the name of your bucket. Example: `PREFIX-orca-archive` and `PREFIX-orca-reports`
  :::note
  Due to limits on report names, the maximum length of a non-report bucket's name is 54 characters.
  :::

:::note

The `--region us-west-2` and `--create-bucket-configuration "LocationConstraint=us-west-2"`
lines are only necessary if you are creating your bucket outside of **us-east-1**.

:::

For more information on creating an S3 bucket, see the
[AWS "Creating a Bucket" documentation](http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html)
and the [Cumulus "Creating an S3 Bucket" documentation](https://nasa.github.io/cumulus/docs/deployment/create_bucket).


## Provide Cross Account (OU) Access

Per best practice, the ORCA archive bucket will be created in the Disaster
Recovery OU and the additional ORCA components will be created in the Cumulus OU.
In order for the components in the Cumulus OU to interact with the ORCA archive
bucket in the Cumulus OU, cross account bucket access privileges are needed. This
section details the steps needed to request the cross account bucket access.

:::warning Deploying ORCA with Objects in Different OUs

If you are following best practice and have created your ORCA archive bucket in
the Disaster Recovery OU, you must have cross account bucket access permissions
created and enabled before deploying the ORCA code. If you do not, your deployment
will return with the following error.

```
module.orca.module.orca_lambdas.aws_s3_bucket_notification.copy_lambda_trigger: Creating...

Error: Error putting S3 notification configuration: AccessDenied: Access Denied
	status code: 403, request id: 2E31C2ACD124B50B, host id: 0JrRBUioe/gT......
```

:::

### Via AWS CloudFormation Template

The AWS Cloudformation template for creating the ORCA DR buckets can be found [here](https://github.com/nasa/cumulus-orca/blob/master/modules/dr_buckets_cloudformation/dr-buckets.yaml). Make sure you have AWS CLI installed before deploying this template.

From your terminal, run the following command by replacing the variables `<PREFIX>` and `<AWS_ACCOUNT_ID>` first:

```
aws cloudformation deploy --stack-name <PREFIX>-orca-bucket-stack --template-file dr-buckets.yaml --parameter-overrides "PREFIX"="<PREFIX>" "CumulusAccountID"="<AWS_ACCOUNT_ID>"

```
This will create archive and reports buckets with the necessary bucket policies giving the Cumulus Account permission to write data to the archive bucket.

### Via Terraform

The Terraform template for creating the ORCA DR buckets can be found [here](https://github.com/nasa/cumulus-orca/blob/master/modules/dr_buckets/dr_buckets.tf). Make sure you have AWS CLI installed and AWS configured to deploy to your DR account.

From your terminal, first run `terraform init` followed by `terraform apply`. When running the apply, Terraform will ask for the following inputs:
1. `cumulus_account_id` - This is the account ID of the Cumulus AWS account.
2. `prefix` - This is the prefix to use for the bucket names.

Tags are an optional variable that can be set if you wish to have the DR buckets tagged.

Optionally you can provide Terraform the required inputs through the terminal with the following:
```
terraform apply \
-var=cumulus_account_id="<CUMULUS_ACCOUNT_ID>" \
-var=prefix="PREFIX"
```

### Via AWS GUI

For each of the buckets listed below
go to AWS, open the bucket in question, click "Permissions", 
then under "Bucket policy" click "Edit".
The policy given, once modified, can be pasted into this form.

##### Archive Bucket:

The policy shown below can be used with some minor
modifications, which will be detailed below.

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
        "Sid": "denyInsecureTransport",
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": [
          "arn:aws:s3:::PREFIX-orca-archive",
          "arn:aws:s3:::PREFIX-orca-archive/*"
        ],
         "Condition": {
         "Bool": {
           "aws:SecureTransport": "false"
           }
         }
      },
      {
         "Sid": "Cross Account Access",
         "Effect": "Allow",
         "Principal": {
            "AWS": "arn:aws:iam::012345678912:root"
         },
         "Action":[
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:RestoreObject",
            "s3:GetBucketVersioning",
            "s3:GetBucketNotification",
            "s3:ListBucket",
            "s3:PutBucketNotification",
            "s3:GetInventoryConfiguration",
            "s3:PutInventoryConfiguration",
            "s3:ListBucketVersions"
         ],
         "Resource": [
            "arn:aws:s3:::PREFIX-orca-archive",
            "arn:aws:s3:::PREFIX-orca-archive/*"
         ]
      },
      {
         "Sid": "Cross Account Write Access",
         "Effect": "Allow",
         "Principal": {
            "AWS": "arn:aws:iam::012345678912:root"
         },
         "Action": "s3:PutObject",
         "Resource": [
            "arn:aws:s3:::PREFIX-orca-archive/*"
         ],
         "Condition": {
            "StringEquals": {
               "s3:x-amz-storage-class": [
                  "GLACIER",
                  "DEEP_ARCHIVE"
               ]
            }
         }
      }
   ]
}
```

The Principal value is the AWS root user for your Cumulus application that will
access the ORCA archive bucket. The value for this can be retrieved by
performing the following.

First, change your connection to the Cumulus account/OU rather than the Disaster Recovery account/OU.
Then, using your AWS CLI client run the following command to get the account number:

```bash
aws sts get-caller-identity

{
    "UserId": "ABCWXYZ123...",
    "Account": "90912...",
    "Arn": "arn:aws:iam::90912...:user/NGAPShApplicationDeveloper-someone-123"
}
```

Replace the number in `arn:aws:iam::012345678912:root` with the value of your non-DR account number.

The Resource value is the bucket and bucket paths that the Cumulus application
can access. Replace `PREFIX-orca-archive` with the name
of the Orca archive bucket created in the previous section.

##### Reports Bucket:

The policy shown below can be used with some minor
modifications, which will be detailed below.

```json
{
  "Version": "2012-10-17",
  "Statement": [
   {
     "Sid": "denyInsecureTransport",
     "Effect": "Deny",
     "Principal": "*",
     "Action": "s3:*",
     "Resource": [
          "arn:aws:s3:::PREFIX-orca-reports",
          "arn:aws:s3:::PREFIX-orca-reports/*"
        ],
     "Condition": {
     "Bool": {
       "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "Cross Account Access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::012345678912:root"
      },
      "Action": [
        "s3:GetObject",
        "s3:GetBucketNotification",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:PutBucketNotification"
      ],
      "Resource": [
        "arn:aws:s3:::PREFIX-orca-reports",
        "arn:aws:s3:::PREFIX-orca-reports/*"
      ]
    },
    {
      "Sid": "Inventory-PREFIX-orca-archive-reports",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::PREFIX-orca-reports/*",
      "Condition": {
        "StringEquals": {
      	  "aws:SourceAccount": "000000000000"
        },
      	"ArnLike": {
      	  "aws:SourceArn": ["arn:aws:s3:::PREFIX-orca-archive"]
      	}
      }
    }
  ]
}
```
The Principal value is the AWS root user for your Cumulus application that will
access the ORCA reports bucket.
See the Archive Bucket instructions for assistance getting this value.

Replace the number in `arn:aws:iam::012345678912:root` with the value of your non-DR account number.
See the Archive Bucket instructions for assistance getting this value.

Replace the number `000000000000` with your DR account number.

The Resource value is the bucket and bucket paths that the Cumulus application
can access. Replace `PREFIX-orca-reports` with the name
of the Orca reports bucket created in the previous section.

Replace `PREFIX-orca-archive` with the name of your [ORCA archive bucket](#archive-bucket).
If you have multiple ORCA buckets, expand the `SourceArn` array with the following format:
```json
"ArnLike": {
   "aws:SourceArn": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME"]
}
```

Replace `PREFIX-orca-archive` with the name of your [ORCA archive bucket](#archive-bucket).
If you have multiple ORCA buckets, expand the `SourceArn` array with the following format:
```json
"ArnLike": {
   "aws:SourceArn": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME"]
}
```

##### Bucket policy for load balancer server access logging:

You must add the following S3 bucket policy to your `system_bucket`, which will likely be named `<PREFIX>-internal`, to give the load balancer access to write logs to the S3 bucket. Otherwise, the deployment will throw an `Access Denied` error. If successful, a test log message will be posted to the bucket under the provided prefix.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<LOAD_BALANCER_ACCOUNT_ID>:root"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::<BUCKET_NAME>/<PREFIX>-lb-gql-a-logs/AWSLogs/<AWS_ACCOUNT_ID>/*"
        }
    ]
}
```
Replace `<LOAD_BALANCER_ACCOUNT_ID>` with the ID of the AWS account for Elastic Load Balancing for your Region which can be found [here](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-access-logs.html#attach-bucket-policy). If you do not know your region name, it can be found [here](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html).

:::note
Note that `<LOAD_BALANCER_ACCOUNT_ID>` is different from your AWS account ID.
:::

Replace `<BUCKET_NAME>` with your `system-bucket` name.

Replace `<PREFIX>` with your prefix.

Replace `<AWS_ACCOUNT_ID>` with your Cumulus OU account number.


For Network Load Balancers you must add the following S3 bucket policy to your `system_bucket`, which will likely be named `<PREFIX>-internal`, to give the load balancer access to write logs to the S3 bucket. Otherwise, the deployment will throw an `Access Denied` error.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
	    "Effect": "Allow",
            "Principal": {
	    "Service": "delivery.logs.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::<BUCKET_NAME>/<PREFIX>-lb-gql-n-logs/AWSLogs/<AWS_ACCOUNT_ID>/*"
        }
    ]
}
```

:::note 

Replace `<BUCKET_NAME>` with your `system-bucket` name.

Replace `<PREFIX>` with your prefix.

Replace `<AWS_ACCOUNT_ID>` with your Cumulus OU account number.
