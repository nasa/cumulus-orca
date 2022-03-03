---
id: research-bamboo-integration-tests
title: Research Notes on running integration tests in bamboo CICD
description: Research Notes on deploying Cumulus and ORCA in bamboo CICD and running integration tests.
---

## Bamboo CICD

Details of some of the intial work done are added in the [ORCA-test-bamboo](https://github.com/nasa/cumulus-orca/tree/feature/ORCA-test-bamboo) branch of `cumulus-orca` repo. The [bamboo spec file](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bamboo-specs/bamboo.yaml#L22) has been modified two add two new stages `Deploy Dev RDS Stack` which deploys the RDS cluster in sandbox and the `Deploy Dev Cumulus and ORCA Stack` stage which deploys the data persistence module as well as cumulus and orca modules. The [deployment-rds.sh](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bin/deployment-rds.sh) script is an intial working script that was used to deploy the RDS cluster. The [deployment-cumulus-orca.sh](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bin/deployment-cumulus-orca.sh) script is an intial script that was used to deploy the data-persistence-tf module. Some changes still need to be made in these scripts to make it more functional and handle errors. A successful bamboo build can be seen [here](https://ci.earthdata.nasa.gov/browse/ORCA-PP-108).
Some of the sensitive bamboo variables such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `RDS_USER_ACCESS_SECRET_ARN` have been encrypted using bamboo encryption service. While running the pipeline, those variables have to be replaced manually with the real values since bamboo does not automatically decrypt the values while running the pipeline.

## Plan for automating integration tests

- Finish successfully deploying all three modules into Bamboo.


## Future directions

- Convert bamboo plans to YAML definition language and store under `cumulus-orca/bamboo-specs/bamboo.yaml`.
- In order to add the webhook to the `cumulus-orca` repo, email `nasa-data@lists.arc.nasa.gov` to NASA Github admin team to make that change. More instructions can be found [here](https://github.com/nasa/instructions/blob/master/docs/INSTRUCTIONS.md#org-owners).


##### References
- https://github.com/nasa/cumulus/tree/master/bamboo

























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
