---
id: research-bamboo-integration-tests
title: Research Notes on running integration tests in bamboo CICD
description: Research Notes on deploying Cumulus and ORCA in bamboo CICD and running integration tests.
---

## Overview

[Bamboo](https://confluence.atlassian.com/bamboo/getting-started-with-bamboo-289277283.html) is a continuous integration (CI) and continuous deployment (CD) server used to automate the release and deployment of software applications. A typical bamboo workflow configuration consists of the following:

 - Plan - It consists of single or multiple stages that are run sequentially using the same repository and defines the build that is triggered.
 - Stage - It consists of single or multiple jobs that run simultaneously.
 - Job - It processes one or more tasks that run simultaneously in an ordered fashion. 
 - Task - It is the actual work that is being executed as part of the build (e.g., running a shell script).

## Bamboo specs

Bamboo Specs are used to write Bamboo configuration as code either in Java or YAML and have corresponding plans/deployments created or updated automatically in Bamboo. YAML specs will be used in ORCA to convert Bamboo specs to code as its configuration is easy to understand. Check [documentation](https://docs.atlassian.com/bamboo-specs-docs/7.0.1/specs.html#starting-with-yaml) for details on the YAML specs.

:::note
A project has to be created manually first in Bamboo since it not possible to create a project with YAML file.
:::

An example of a bamboo config spec in YAML is shown below. This plan named `test-orca` consists of a manual stage named `orca test stage` which consists of a job named `orca test job`. This `orca test job` has a task that runs a shell script. 

```yaml
---
version: 2
plan:
  project-key: ORCA
  key: ORCA
  name: test-orca
stages:
- orca test stage:
    manual: true
    jobs:
    - orca test job
orca test job:
  key: OTJ
  tasks:
  - script:
      interpreter: SHELL
      scripts:
      - |-
        set -ex
        echo "hello"
```

### Bamboo configuration
Some of the important configuration parameters used to create a Bamboo plan is described below:

- Triggers- This is used to automatically run a bamboo plan. Users can specify how and when the build will be triggered. Some of the different types of triggers include repository polling, remote trigger, scheduled trigger, single day build trigger and tag trigger. Currently, ORCA uses `repository polling` trigger that polls source repository and builds when new changes are found. In this example, Bamboo will check the repository for changes every 60 seconds and automatically build it when changes are detected.

```yaml
triggers:
- polling:
    period: '60'
```

- Repositories- One or more repositories can be added to a plan, which will be available to every job in the plan. The first repository in the list is the plan’s default repository. An example of how a repository can be added to a bamboo plan is shown below. 

```yaml
repositories:
- ORCA repo:
    type: git
    url: https://github.com/nasa/cumulus-orca
    branch: develop
```
- Branches - Plan branches allow the user to run builds across different branches in the source repository using the same plan configuration.
In the example below, this pipeline will use the same plan when new branches are created in the repo and also link to a Jira issue if the branch name contains a Jira issue key.

```yaml
branches:
  create: for-new-branch
  delete:
    after-deleted-days: 7
    after-inactive-days: 30
  link-to-jira: true
```

- Variables- Variables are used to substitute values in the task config and inline scripts. To use in task scripts, use the syntax `${bamboo.variable_name}` and replace variable_name with yours. An example of using variables in a plan is shown below.
```yaml
variables:
  ORCA_VERSION: 0.0.1
  RELEASE_FLAG: 'false'
```
- Permissions- Permissions are used to restrict access to specific users to a Bamboo plan. In the following example, only the user rhassan can do some specific actions on this plan.

```yaml
version: 2
plan:
  key: ORCA
plan-permissions:
- users:
  - rhassan
  permissions:
  - view
  - edit
  - build
  - clone
  - admin
```
- Docker- It is also possible to run a job inside a docker image rather than the bamboo agent if required. Check this [documentation](https://hub.docker.com/r/atlassian/bamboo-agent-base) for more information.

```yaml
test job name:
  key: TJN
  docker:
    image: alpine
```
- Artifact- Artifacts are files created by a job build that can be used in other stages. An artifact definition can be created to specify which artifacts to keep and share from a build job. In the example below, an artifact definition named `test-artifact` is created under the job `test job` which is shared with other builds and deployments. Only the file matching the pattern .xml will be stored under artifact directory. 

```yaml
test job:
  artifacts:
  - name: test-artifact
    location: artifact
    pattern: '*.xml'
    shared: true
```
Check artifact [documentation](https://confluence.atlassian.com/bamboo/configuring-a-job-s-build-artifacts-289277071.html) for more information.

- Checkout- This is a task to check out a repository for use by just one job. In the example below, the job named `test job` has a checkout task that will checkout to the default repo defined in the plan before the tasks executes.

```yaml
test job:
  tasks:
  - checkout:
      description: Checkout Default Repository
```
Check this [documentation](https://confluence.atlassian.com/bamboo0800/checking-out-code-1077778795.html) for more information.


## Running Bamboo specs
In order to run the YAML definition file, it has to be stored at `bamboo-specs/bamboo.yml` or `bamboo-specs/bamboo.yaml`under the repository specified. Check this [documentation](https://confluence.atlassian.com/bamboo/bamboo-yaml-specs-938844479.html) for more information.

:::important
Make sure the linked repository have permissions to create plans within given project in order to execute the YAML definition and create a plan. 
:::

In order to run this YAML definition from github repo, user has to setup `Repository-stored Specs` on Bamboo CI/CD [website](https://ci.earthdata.nasa.gov/build/admin/create/newSpecs.action). From the Bamboo dashboard, Choose `Specs`->`Set up Specs repository` and then select `Build project` as `ORCA` and `Repository host` as `ORCA repo`.
The next step is to create a `Webhook` on the source repository by going to the settings option so that Bamboo knows about new commits. Webhooks allow Github repositories to communicate with Bamboo. A webhook has been created for [ORCA project](https://ci.earthdata.nasa.gov/browse/ORCA) in Bamboo which needs to be copied to the `webhook` section in cumulus-orca repo. The webhook can be seen under the `Specs` section on Bamboo CI website. Without adding webhook, Bamboo was not able to recognize the new Spec file added to the `cumulus-orca` repo. Email `nasa-data@lists.arc.nasa.gov` to NASA Github admin team to make that change. More instructions can be found [here](https://github.com/nasa/instructions/blob/master/docs/INSTRUCTIONS.md#org-owners)
:::important
 Webhooks must be triggered by HTTP POST method and the Content-Type header should be set to `application/json`.
:::
If Webhook is not created, then user has to `set up Specs repository` as shown above every time the YAML definition is changed. Otherwise, it will not pull the latest changes. Check this [documentation](https://confluence.atlassian.com/bamboo0800/enabling-webhooks-1077778691.html) for details on setting up Webhook.

## Creating a prototype

A prototype using Bamboo has been created [here](https://ci.earthdata.nasa.gov/browse/ORCA-PROTOTYPE). Make sure NASA VPN is connected and that you have access to ORCA project on CI site.
Code for the prototype resides currently in this [branch](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bamboo-specs/bamboo.yaml) since we do not want to merge this into develop.

## Future directions

- Convert bamboo plans to YAML definition language and store under `cumulus-orca/bamboo-specs/bamboo.yaml`.
- In order to add the webhook to the `cumulus-orca` repo, email `nasa-data@lists.arc.nasa.gov` to NASA Github admin team to make that change. More instructions can be found [here](https://github.com/nasa/instructions/blob/master/docs/INSTRUCTIONS.md#org-owners).


##### References
- https://confluence.atlassian.com/bamboo/understanding-the-bamboo-ci-server-289277285.html
- https://confluence.atlassian.com/bamboo/bamboo-yaml-specs-938844479.html
- https://docs.atlassian.com/bamboo-specs-docs/7.0.1/specs.html
- https://ci.earthdata.nasa.gov/
- https://confluence.atlassian.com/bamboo0800/enabling-webhooks-1077778691.html

























https://github.com/nasa/cumulus/blob/master/bamboo/bootstrap-tf-deployment.sh


deploy cumulus and orca first in bamboo
then run scripts for integration tests
different scripts for each tests

cumulus uses their own docker image at maven.earthdata.nasa.gov/cumulus:latest

#!/bin/bash
set -ex

apt-get update
apt-get install -y python-pip
pip install awscli

TF_VERSION=$(cat .tfversion)
# Fetch terraform binary
if ! curl -o terraform_${TF_VERSION}_linux_amd64.zip https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip ; then
  echo "ERROR: coudn't download terraform script" >&2
  exit 1
else
  unzip -u ./terraform_${TF_VERSION}_linux_amd64.zip
  chmod a+x ./terraform
  rm ./terraform_${TF_VERSION}_linux_amd64.zip
fi

DATA_PERSISTENCE_KEY="$DEPLOYMENT/data-persistence/terraform.tfstate"
cd data-persistence-tf
# Ensure remote state is configured for the deployment
echo "terraform {
  backend \"s3\" {
    bucket = \"$TFSTATE_BUCKET\"
    key    = \"$DATA_PERSISTENCE_KEY\"
    region = \"$AWS_REGION\"
    dynamodb_table = \"$TFSTATE_LOCK_TABLE\"
  }
}" >> ci_backend.tf

# Initialize deployment
../terraform init \
  -input=false

if [[ $NGAP_ENV = "SIT" ]]; then
  BASE_VAR_FILE="sit.tfvars"
  CMA_LAYER_VERSION=17
  ROLE_BOUNDARY=NGAPShRoleBoundary
else
  BASE_VAR_FILE="sandbox.tfvars"
  CMA_LAYER_VERSION=20
  ROLE_BOUNDARY=NGAPShNonProdRoleBoundary
fi

# Deploy data-persistence-tf via terraform
echo "Deploying Cumulus data-persistence module to $DEPLOYMENT"
../terraform apply \
  -auto-approve \
  -input=false \
  -var-file="../deployments/data-persistence/$BASE_VAR_FILE" \
  -var-file="../deployments/data-persistence/$DEPLOYMENT.tfvars" \
  -var "aws_region=$AWS_REGION" \
  -var "subnet_ids=[\"$AWS_SUBNET\"]" \
  -var "vpc_id=$VPC_ID" \
  -var "rds_admin_access_secret_arn=$RDS_ADMIN_ACCESS_SECRET_ARN" \
  -var "rds_security_group=$RDS_SECURITY_GROUP"\
  -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$ROLE_BOUNDARY"

cd ../cumulus-tf
# Ensure remote state is configured for the deployment
echo "terraform {
  backend \"s3\" {
    bucket = \"$TFSTATE_BUCKET\"
    key    = \"$DEPLOYMENT/cumulus/terraform.tfstate\"
    region = \"$AWS_REGION\"
    dynamodb_table = \"$TFSTATE_LOCK_TABLE\"
  }
}" >> ci_backend.tf

# Initialize deployment
../terraform init \
  -input=false

# Deploy cumulus-tf via terraform
echo "Deploying Cumulus example to $DEPLOYMENT"
../terraform apply \
  -auto-approve \
  -input=false \
  -var-file="../deployments/cumulus/$BASE_VAR_FILE" \
  -var-file="../deployments/cumulus/$DEPLOYMENT.tfvars" \
  -var "cumulus_message_adapter_lambda_layer_version_arn=arn:aws:lambda:us-east-1:$AWS_ACCOUNT_ID:layer:Cumulus_Message_Adapter:$CMA_LAYER_VERSION" \
  -var "cmr_username=$CMR_USERNAME" \
  -var "cmr_password=$CMR_PASSWORD" \
  -var "cmr_client_id=cumulus-core-$DEPLOYMENT" \
  -var "cmr_provider=CUMULUS" \
  -var "cmr_environment=UAT" \
  -var "csdap_client_id=$CSDAP_CLIENT_ID" \
  -var "csdap_client_password=$CSDAP_CLIENT_PASSWORD" \
  -var "launchpad_passphrase=$LAUNCHPAD_PASSPHRASE" \
  -var "data_persistence_remote_state_config={ region: \"$AWS_REGION\", bucket: \"$TFSTATE_BUCKET\", key: \"$DATA_PERSISTENCE_KEY\" }" \
  -var "region=$AWS_REGION" \
  -var "vpc_id=$VPC_ID" \
  -var "lambda_subnet_ids=[$AWS_LAMBDA_SUBNET]" \
  -var "urs_client_id=$EARTHDATA_CLIENT_ID" \
  -var "urs_client_password=$EARTHDATA_CLIENT_PASSWORD" \
  -var "token_secret=$TOKEN_SECRET" \
  -var "permissions_boundary_arn=arn:aws:iam::$AWS_ACCOUNT_ID:policy/$ROLE_BOUNDARY" \
  -var "pdr_node_name_provider_bucket=$PDR_NODE_NAME_PROVIDER_BUCKET" \
  -var "rds_admin_access_secret_arn=$RDS_ADMIN_ACCESS_SECRET_ARN" \
  -var "orca_db_user_password=$ORCA_DATABASE_USER_PASSWORD" \
