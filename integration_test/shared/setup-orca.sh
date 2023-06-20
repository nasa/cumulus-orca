#!/bin/bash

echo "Hello"
export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION

export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')

export orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaCopyToArchiveWorkflow"
export orca_RECOVERY_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${bamboo_PREFIX}-OrcaRecoveryWorkflow"

echo $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
echo $orca_RECOVERY_STEP_FUNCTION_ARN

aws stepfunctions   describe-state-machine --state-machine-arn $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN