#!/bin/bash
set -ex
cwd=$(pwd)

export orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:{$bamboo_PREFIX}-OrcaCopyToArchiveWorkflow"
export orca_RECOVERY_STEP_FUNCTION_ARN="arn:aws:states:${bamboo_AWS_DEFAULT_REGION}:${AWS_ACCOUNT_ID}:stateMachine:{$bamboo_PREFIX}-OrcaRecoveryWorkflow"

echo $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
echo $orca_RECOVERY_STEP_FUNCTION_ARN

aws stepfunctions   describe-state-machine --state-machine-arn $orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
