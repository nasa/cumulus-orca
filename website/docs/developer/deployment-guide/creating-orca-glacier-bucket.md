---
id: deployment-s3-bucket
title: Creating the Glacier Bucket
description: Provides developer with information on archive storage solutions.
---

ORCA maintains a cloud ready backup of science and ancillary data in an
[S3-IA](https://aws.amazon.com/s3/storage-classes/#Infrequent_access)
bucket and utilizes [AWS bucket transition policies](https://docs.aws.amazon.com/AmazonS3/latest/dev/lifecycle-transition-general-considerations.html)
to store the data in [S3 Glacier](../../about/introduction/glossary.md#glacier-storage)
for the long term. The ORCA archive bucket can live in any NGAP Organizational
Unit (OU).

:::important ORCA S3 Glacier Bucket OU Placement

Best practice is to place the ORCA archive bucket in your Disaster Recovery OU.
This is done to better separate the costs associated with the cloud ready backup
from primary Cumulus holdings and ingest and archive activity. See the
[ORCA Architecture Introduction documentation](../../about/architecture/architecture-intro.mdx)
for more information.

:::

The sections below go into further detail on creating the ORCA archive bucket.

## Create the ORCA Archive Bucket

Prior to creating the S3 bucket, make sure the deployment environment is created
per the [Creating the Deployment Environment](setting-up-deployment-environment.mdx)
documentation.

To create the ORCA archive bucket run the AWS CLI command below and replace the
\[place holder text\] with proper values for your deployment.

```bash
aws s3api create-bucket \
    --bucket [orca bucket name] \
    --profile [AWS OU profile]  \
    --region us-west-2 \
    --create-bucket-configuration "LocationConstraint=us-west-2"
```

- **\[orca bucket name\]** - This is the name of your ORCA archive bucket. Example: sandbox-orca-glacier-archive
- **\[AWS OU profile\]** - This is the AWS profile name to use to connect to the proper OU where the bucket will be created.

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

### Filling out the form

First, create a NASD ticket for cross account bucket access. This is a turn key
request to NGAP. The link to create a ticket is available
[here](https://bugs.earthdata.nasa.gov/servicedesk/customer/portal/7/create/80).

Next, fill out the form. The sections below provide information on the data needed
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
> the ORCA DR account S3 bucket in order to create an operational archive copy of
> ORCA data and recover data back to the primary Cumulus data holdings in case
> of a failure. This cross account access will allow the Cumulus application to
> seamlessly perform these functions and provide operators with the capability to
> test and verify disaster recovery scenarios.


#### Bucket Names(s):

This is the name of the ORCA archive bucket created in the Disaster Recover OU.
Below is an example name of an ORCA archive bucket and ORCA report bucket.

> sandbox-orca-glacier-archive
> sandbox-orca-reports


#### Policy:

The policy section is the JSON policy requested for the ORCA archive bucket in
the Disaster Recovery OU. The policy shown below can be used with some minor
modifications, which will be detailed below.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Cross Account Access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::909121343565:root"
      },
      "Action": [
        "s3:GetObject*",
        "s3:RestoreObject",
        "s3:GetBucket*",
        "s3:ListBucket",
        "s3:PutBucketNotification",
        "s3:GetInventoryConfiguration",
        "s3:PutInventoryConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::sandbox-orca-glacier-archive",
        "arn:aws:s3:::sandbox-orca-glacier-archive/*"
      ]
    },
    {
      "Sid": "Cross Account Write Access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::909121343565:root"
      },
      "Action": "s3:PutObject*",
      "Resource": [
        "arn:aws:s3:::sandbox-orca-glacier-archive/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
```

The Principal value is the AWS root user for your Cumulus application that will
access the ORCA archive bucket. The value for this resource can be retrieved by
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

Replace the number in `arn:aws:iam::909121343565:root` with the value of your
account number.

The Resource value is the bucket and bucket paths that the Cumulus application
can access. Replace `arn:aws:s3:::sandbox-orca-glacier-archive` with the name
of the Orca archive bucket created in the previous section.


