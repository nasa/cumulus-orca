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

## Creating all you need with a Cloud Formation Template

Apply the following cloud formation template to your DR account with the following inputs:
- DAAC, your Cumulus DAAC. For example, obdaac
- Maturity. For example, sit,uat or prod
- Cumulus Account ID, the account ID of the Cumulus account that will backup data into ORCA

This will create archive and reports buckets with the necessary bucket policies giving the Cumulus Account permission to write data to the archive bucket.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: 'AWS CloudFormation Template for ORCA bucket creation:
  ORCA requires the creation of two S3 buckets. One for archival an one for reporting.
  Both buckets require cross account access so that the corresponding Cumulus account can access the bucket. 
  In the case of the reporting bucket, the ORCA account requires access too.'
Parameters:
  DAAC:
    Type: String
    Description: 'The name of the S3 Bucket to create, make this unique'
  Maturity:
    Type: String
    Description: 'sit, uat or prod'
    AllowedValues: ["sit", "uat", "prod"]
  CumulusAccountID:
    Type: String
    Description: 'The account ID of the Cumulus account that requires access'
Resources:
  S3ARCHBUCKET:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: !Sub '${DAAC}-${Maturity}-orca-archive'
  S3ARCHBUCKETPOL:
    Type: 'AWS::S3::BucketPolicy'
    Properties:
      Bucket: !Sub '${DAAC}-${Maturity}-orca-archive'
      PolicyDocument:
        Id: "Cross Account Access"
        Version: "2012-10-17"
        Statement:
          - Sid: CrossAccPolicyDoc
            Action: [
              "s3:GetObject*",
              "s3:RestoreObject",
              "s3:GetBucket*",
              "s3:ListBucket",
              "s3:PutBucketNotification",
              "s3:GetInventoryConfiguration",
              "s3:PutInventoryConfiguration",
              "s3:ListBucketVersions"
            ]
            Effect: Allow
            Resource: [
              !Sub 'arn:aws:s3:::${S3ARCHBUCKET}',
              !Sub 'arn:aws:s3:::${S3ARCHBUCKET}/*'
            ]
            Principal:
              AWS: !Join ['', ["arn:aws:iam::", !Ref CumulusAccountID, ":root"]]
          - Sid: "Cross Account Write Access"
            Action: "s3:PutObject*"
            Effect: Allow
            Resource: !Sub 'arn:aws:s3:::${S3ARCHBUCKET}/*'
            Condition:
              StringNotEquals:
                's3:x-amz-storage-class':
                  - 'GLACIER'
                  - 'DEEP_ARCHIVE'
                's3:x-amz-acl': 'bucket-owner-full-control'
            Principal:
              AWS: !Join ['', ["arn:aws:iam::", !Ref CumulusAccountID, ":root"]]
    DependsOn: S3ARCHBUCKET
  S3REPBUCKET:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketName: !Sub '${DAAC}-${Maturity}-orca-reports'
  S3REPBUCKETPOL:
    Type: 'AWS::S3::BucketPolicy'
    Properties:
      Bucket: !Sub '${DAAC}-${Maturity}-orca-reports'
      PolicyDocument:
        Id: "Cross Account Access"
        Version: "2012-10-17"
        Statement:
          - Sid: CrossAccPolicyDoc
            Action: [
              "s3:GetObject*",
              "s3:GetBucket*",
              "s3:ListBucket",
              "s3:PutObject",
              "s3:PutObjectAcl",
              "s3:PutBucketNotification"
            ]
            Effect: Allow
            Resource: [
              !Sub 'arn:aws:s3:::${S3REPBUCKET}',
              !Sub 'arn:aws:s3:::${S3REPBUCKET}/*'
            ]
            Principal:
              AWS: !Join ['', ["arn:aws:iam::", !Ref CumulusAccountID, ":root"]]
          - Sid: !Sub 'Inventory-${DAAC}-${Maturity}-orca-reports'
            Action: "s3:PutObject"
            Effect: Allow
            Resource: !Sub 'arn:aws:s3:::${S3REPBUCKET}/*'
            Condition: 
              StringEquals:
                's3:x-amz-acl': 'bucket-owner-full-control'
                'aws:SourceAccount': !Ref AWS::AccountId
              ArnLike:
                aws:SourceArn: !Sub 'arn:aws:s3:::${DAAC}-${Maturity}-orca-reports'
            Principal:
              Service: "s3.amazonaws.com"
    DependsOn: S3REPBUCKET 
Outputs:
  ArchiveBucket:
    Description: Archive S3 Bucket Name
    Value: !Ref S3ARCHBUCKET
  ArchiveBucketPolicy:
    Description: Archive S3 Bucket Policy Name
    Value: !Ref S3ARCHBUCKETPOL
  ReportsBucket:
    Description: Archive S3 Bucket Name
    Value: !Ref S3REPBUCKET
  ReportsBucketPolicy:
    Description: Archive S3 Bucket Policy Name
    Value: !Ref S3REPBUCKETPOL
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
         "Sid": "Cross Account Access",
         "Effect": "Allow",
         "Principal": {
            "AWS": "arn:aws:iam::012345678912:root"
         },
         "Action":[
            "s3:GetObject*",
            "s3:RestoreObject",
            "s3:GetBucket*",
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
         "Action": "s3:PutObject*",
         "Resource": [
            "arn:aws:s3:::PREFIX-orca-archive/*"
         ],
         "Condition": {
            "StringEquals": {
               "s3:x-amz-acl": "bucket-owner-full-control",
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

### Via NGAP form

If your accounts are both within EDC, you may skip to [the primary method](#via-aws-gui).
Otherwise, create a NASD ticket for cross account bucket access.
This is a turn key request to NGAP. The link to create a ticket is available
[here](https://bugs.earthdata.nasa.gov/servicedesk/customer/portal/7/create/85).

The sections below provide information on the data needed
for each of the fields and where to look for information.

#### Project Name

This is the name of the Disaster Recover OU where the ORCA archive bucket resides.
The project name can be found in your [Cloud Tamer](http://cloud.earthdata.nasa.gov/)
account and is usually in the format of \[project name\]-app-\[application name\]-\[environment\]-\[4 digit number\].
For example, an ORCA disaster recovery OU project name may look like the following
orca-app-dr-sandbox-1234.

#### Account Type:

This is the OU environment the bucket resides in. Typical values for this field
are Sandbox, SIT, UAT, and Production.

#### Business Justification:

This is the business justification for the cross account bucket access. Below is
an example of a justification.

> The ORCA Cumulus application in the Cumulus Sandbox OU needs to read/write to
> the ORCA DR account S3 buckets in order to create an operational archive copy of
> ORCA data and recover data back to the primary Cumulus data holdings in case
> of a failure. Note that only `GLACIER` and `DEEP_ARCHIVE` storage types are allowed for objects written to the bucket. This cross account access will allow the Cumulus application to
> seamlessly perform these functions and provide operators with the capability to
> test and verify disaster recovery scenarios.

#### Bucket Names(s):

This is the name of the ORCA archive bucket created in the Disaster Recover OU.
Below is an example name of an ORCA archive bucket and ORCA report bucket.

> PREFIX-orca-archive
> PREFIX-orca-reports

#### Policy:

The policy section is the JSON policy requested for the ORCA archive bucket in
the Disaster Recovery OU.
See [the section below](#via-aws-gui) for policy document examples.

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
      	  "s3:x-amz-acl": "bucket-owner-full-control",
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