---
id: deployment
title: Deployment Information
description: Provides developer information for ORCA code deployment.
---

## Introduction to ORCA
The Operational Recovery Cloud Archive (ORCA) provides 
a baseline solution for creating, and managing 
operational backups in the cloud. In addition, best
practices and recovery code that manages common 
baseline recovery scenarios is also maintained.


## Deploying ORCA
The following sections provide information on how to
deploy ORCA with or along-side Cumulus.
### Setup Deployment Environment
In order to deploy ORCA into an NGAP environment with 
Cumulus, a deployment environment needs be created.

Visit [Creating a Deployment Environment](setting-up-deployment-environment.md)
to view the instructions for setting up your ORCA deployment environment.

### ORCA Archive Bucket
ORCA maintains a cloud ready backup of science and 
ancillary data in an S3-IA bucket and utilizes AWS 
bucket transition policies to store the data in S3 
Glacier for the long term. The ORCA archive bucket can 
live in any NGAP Organizational Unit (OU).

Visit [Creating the Glacier Bucket](creating-orca-glacier-bucket.md)
to view the instructions for setting up a Glacier 
bucket.

:::important
Prior to deploying ORCA with Cumulus, the ORCA archive bucket must be
created.
:::

### Deploy ORCA with Cumulus
After the ORCA archive bucket has been created, ORCA is ready to be
deployed. Visit [ORCA deployment documentation](deployment-with-cumulus.md)
for instructions to deploy ORCA with Cumulus.


## Configuring ORCA
Once ORCA is deployed, configure the collection in the Cumulus 
Dashboard for utilizing ORCA. See ORCA Configuration for 
instructions.

