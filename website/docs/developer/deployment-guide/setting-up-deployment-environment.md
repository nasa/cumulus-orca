---
id: deployment-environment
title: Creating a Deployment Environment
description: Provides developer with information on setting up deployment environment.
---

In order to deploy ORCA into an NGAP environment with Cumulus, a deployment
environment needs be created. The sections below describe the tool chain needed
and any additional environmental setup that should occur. The setup for deploying
ORCA is similar to the [Cumulus deployment requirements](https://nasa.github.io/cumulus/docs/deployment/deployment-readme#requirements).
The sections below assume that the end user is using a Linux or MacOS environment.


## Deployment Tool Requirements

The following tools should be installed to perform an ORCA deployment.

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- zip/unzip
- [AWS CLI](https://aws.amazon.com/cli/)
- [AWS CLI Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
- [Terraform Version Manager](https://github.com/tfutils/tfenv)
- [Terraform](https://www.terraform.io/intro/index.html) v0.13.6 and up. Please see the [installing terraform instructions](#installing-terraform).


## Deployment Environment Setup

Setting up the development environment consists of installing the proper Terraform
version using Terraform Version Manager and creating the AWS profiles for connecting
to the proper NGAP OU for your application.


### Installing Terraform

Using Terraform Version Manager install the latest supported version of terraform
using the command below.

```bash
tfenv install 0.13.6
```


### Configure AWS CLI Profiles

Configure the AWS CLI with two profiles. The first profile should be the default
and the access information should be for the Cumulus OU. The second profile should
be have access information for the Disaster Recovery OU.

Use the [Cloud Tamer](https://cloud.earthdatacloud.nasa.gov) application to create
long term access keys to both the Cumulus and Recovery OU environments. Using the
Access Key ID and Secret Access Key values configure the different profiles as seen
below.

**Creating the Default Profile.**
```bash
aws configure --profile default

AWS Access Key ID []: Your AWS Access Key ID Value for Cumulus OU
AWS Secret Access Key []: Your AWS Secret Access Key Value for Cumulus OU
Default region name []: us-west-2
Default output format []: json
```

**Creating the Disaster Recovery Profile**
```bash
aws configure --profile drou-sandbox

AWS Access Key ID []: Your AWS Access Key ID Value for Disaster Recovery OU
AWS Secret Access Key []: Your AWS Secret Access Key Value for Disaster Recovery OU
Default region name []: us-west-2
Default output format []: json
```
