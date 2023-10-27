#!/bin/bash

echo "Hello"
export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION
# buckets structure tied to buckets.tf.template and dr-buckets.tf.template
export orca_BUCKETS='{"protected": {"name": "'$bamboo_PREFIX'-protected", "type": "protected"}, "internal": {"name": "'$bamboo_PREFIX'-internal", "type": "internal"}, "private": {"name": "'$bamboo_PREFIX'-private", "type": "private"}, "public": {"name": "'$bamboo_PREFIX'-public", "type": "public"}, "orca_default": {"name": "'$bamboo_PREFIX'-orca-primary", "type": "orca"}, "provider": {"name": "orca-sandbox-s3-provider", "type": "provider"}}'

# Setting environment variables with proper values
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
export VPC_ID=$(aws ec2 describe-vpcs | jq -r '.Vpcs | to_entries | .[] | .value.VpcId')
export AWS_SUBNET_ID1=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2a"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID2=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2b"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID3=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2c"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaCopyToArchiveWorkflow"
export orca_RECOVERY_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaRecoveryWorkflow"
export orca_RECOVERY_BUCKET_NAME="${bamboo_PREFIX}-orca-primary"

export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')

export orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaCopyToArchiveWorkflow"
export orca_RECOVERY_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaRecoveryWorkflow"

echo $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
echo $orca_RECOVERY_STEP_FUNCTION_ARN

aws stepfunctions   describe-state-machine --state-machine-arn $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
