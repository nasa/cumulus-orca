---
id: intro-glossary
title: Glossary
description: Glossary of terms used in ORCA
---
# ORCA Glossary


## A
### API Gateway
Refers to [AWS's API Gateway](https://aws.amazon.com/api-gateway/). Used by the Cumulus API.

### ARN
Refers to an AWS "Amazon Resource Name". For more info, see the [AWS documentation](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html).

### AWS
See: [aws.amazon.com](https://aws.amazon.com/)

### AWS Lambda/Lambda Function
AWS's 'serverless' option. Allows the running of code without provisioning
a service or managing server/ECS instances/etc.

For more information, see the [AWS Lambda documentation](https://aws.amazon.com/lambda/).

### AWS Access Keys
Access credentials that give you access to AWS to act as a IAM user
programmatically or from the command line. For more information,
see the [AWS IAM Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).


## B
### Bucket
An Amazon S3 cloud storage resource.

For more information, see the [AWS Bucket Documentation](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html).


## C
### Cloudwatch
AWS service that allows logging and metrics collections on various cloud
resources you have in AWS.

For more information, see the [AWS User Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html).

### Cloud Nofification Mechanism (CNM)
An interface mechanism to support cloud-based ingest messaging. For more
information, see [PO.DAAC's CNM Schema](https://github.com/podaac/cloud-notification-message-schema).

### Common Metadata Repository (CMR)
"A high-performance, high-quality, continuously evolving metadata system
that catalogs Earth Science data and associated service metadata records".

For more information, see [NASA's CMR page](https://cmr.earthdata.nasa.gov/).

### Collection (Cumulus)
Cumulus Collections are logical sets of data objects of the same data type
and version.

### Cumulus
A Cloud-based data ingest, archive, distribution, and management system.
See [https://github.com/nasa/cumulus](https://github.com/nasa/cumulus).

### Cumulus Message Adapter (CMA)
A library designed to help task developers integrate step function tasks into
a Cumulus workflow by adapting task input/output into the Cumulus Message
format.

For more information, see [CMA workflow reference page](https://nasa.github.io/cumulus/docs/workflows/input_output#cumulus-message-adapter).


## D
### Distributed Active Archive Center (DAAC)
Refers to a specific organization that's part of NASA's distributed system of
archive centers. For more information see [EOSDIS's DAAC page](https://earthdata.nasa.gov/about/daacs).

### Dead Letter Queue (DLQ)
This refers to Amazon SQS Dead-Letter Queues - these SQS queues are
specifically configured to capture failed messages from other services/SQS
queues/etc to allow for processing of failed messages.

For more on DLQs, see the [Amazon Documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
and the [Cumulus DLQ feature page](https://nasa.github.io/cumulus/docs/features/dead_letter_queues).


## E
### Elastic Container Service (ECS)
Amazon's Elastic Container Service. Used in Cumulus by workflow steps that
require more flexibility than Lambda can provide.

For more information, see [AWS's developer guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html).

### ECS Activity
An ECS instance run via a Step Function.

### EMS
[ESDIS Metrics System](https://earthdata.nasa.gov/about/science-system-description/eosdis-components/esdis-metrics-system-ems)

### Execution (Cumulus)
A Cumulus execution refers to a single execution of a (Cumulus) Workflow.


## F


## G
### GIBS
[Global Imagery Browse Services](https://earthdata.nasa.gov/about/science-system-description/eosdis-components/global-imagery-browse-services-gibs)

### Glacier Storage
[Amazon S3 Glacier](https://aws.amazon.com/glacier/) is a secure,
durable, and extremely low-cost [cloud storage service](https://docs.aws.amazon.com/amazonglacier/latest/dev/introduction.html) 
for data archiving and long-term backup.

### Granule
A granule is the smallest aggregation of data that can be independently
managed (described, inventoried, and retrieved). Granules are always
associated with a collection, which is a grouping of granules. A granule is
a grouping of data files.


## H


## I
### Identity and Access Management (IAM)
AWS Identity and Access Management.

For more information, see [AWS IAMs](https://aws.amazon.com/iam/).


## J


## K
### Kinesis
Amazon's platform for streaming data on AWS.

See [AWS Kinesis](https://docs.aws.amazon.com/kinesis/index.html) for more information.


## L
### Lambda
AWS's cloud service that lets you run code without provisioning or managing
servers.

For more information, see [AWS's lambda page](https://aws.amazon.com/lambda/).


## M
### Module (Terraform)
Refers to a [terraform module](https://www.terraform.io/docs/configuration/modules.html).


## N
### NGAP
NASA General Application Platform. NGAP provides a cloud-based
Platform-as-a-Service (PaaS) and Infrastructure-as-a-Service (IaaS) for
ESDIS applications.
### Node
See [node.js](https://nodejs.org/en/about).

### NPM
Node package manager.

For more information, see [npmjs.com](https://www.npmjs.com/).


## O
### Operator
Refers to those tasked with monitoring, configuring or otherwise utilizing
umulus in an operational deployment.

### ORCA
Operational Recovery Cloud Archive. See [https://github.com/nasa/cumulus-orca](https://github.com/nasa/cumulus-orca)

### OU
AWS Organizational Unit. More information on OUs can be found [here](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html).

## P
### PDR
"Polling Delivery Mechanism" used in "DAAC Ingest" workflows.

For more information, see [nasa.gov](https://earthdata.nasa.gov/esdis/eso/standards-and-references/polling-with-delivery-record-pdr-mechanism).

### Packages (NPM)
[NPM](https://www.npmjs.com/) hosted node.js packages. Cumulus packages can
be found on NPM's site [here](https://www.npmjs.com/org/cumulus).

### Provider
Data source that generates and/or distributes data for Cumulus workflows to
act upon.

For more information, see the [Cumulus documentation](https://nasa.github.io/cumulus/docs/data-cookbooks/setup#providers).

### Python
See [Python.org](https://www.python.org/).


## Q


## R
### Rule
Rules are configurable scheduled events that trigger workflows based on
various criteria.

For more information, see the [Cumulus Rules documentation](https://nasa.github.io/cumulus/docs/data-cookbooks/setup#rules).


## S
### S3
Amazon's Simple Storage Service provides data object storage in the cloud.
Used in Cumulus to store configuration, data and more.

For more information, see [AWS's S3 page](https://aws.amazon.com/s3/).

### SIPS
Science Investigator-led Processing Systems. In the context of DAAC ingest,
this refers to data producers/providers.

For more information, see [nasa.gov](https://earthdata.nasa.gov/about/sips).

### SNS
Amazon's Simple Notification Service provides a messaging service that allows
publication of and subscription to events. Used in Cumulus to trigger workflow
events, track event failures, and others.

For more information, see [AWS's SNS page](https://aws.amazon.com/sns/).

### SQS
Amazon's Simple Queue Service.

For more information, see [AWS's SQS page](https://aws.amazon.com/sqs/).

### Stack
A collection of AWS resources you can manage as a single unit.

In the context of Cumulus, this refers to a deployment of the cumulus and
data-persistence modules that is managed by Terraform.

### Step Function
AWS's web service that allows you to compose complex workflows as a state
machine comprised of tasks (Lambdas, activities hosted on EC2/ECS, some AWS
service APIs, etc). See [AWS's Step Function Documentation](https://aws.amazon.com/step-functions/)
for more information. In the context of Cumulus these are the underlying AWS
service used to create Workflows.


## T

## U


## V
### Virtual Environment (venv)
A contained environment for building/running Python code.
See [Setting Up a Dev Environment](../../developer/development-guide/code/setup-dev-env.md) for more information.


## W
### Workflows
[Workflows](https://nasa.github.io/cumulus/docs/workflows/workflows-readme)
are comprised of one or more AWS Lambda Functions and ECS Activities to
discover, ingest, process, manage and archive data.


## X


## Y


## Z
