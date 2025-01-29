
### Running integration tests locally

The steps to run ORCA integration tests locally are shown below:

1. [Deploy ORCA to AWS](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus).
2. Connect to the NASA VPN.
3. Set the following environment variables:
   1. `orca_API_DEPLOYMENT_INVOKE_URL` Output from the ORCA TF module. ex: `https://0000000000.execute-api.us-west-2.amazonaws.com`
   2. `orca_RECOVERY_STEP_FUNCTION_ARN` ARN of the recovery step function. ex: `arn:aws:states:us-west-2:000000000000:stateMachine:PREFIX-OrcaRecoveryWorkflow`
   3. `orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN` ARN of the copy_to_archive step function. ex: `arn:aws:states:us-west-2:000000000000:stateMachine:PREFIX-OrcaCopyToArchiveWorkflow`
   4. `orca_INTERNAL_RECONCILIATION_STEP_FUNCTION_ARN` ARN of the get_current_archive_list and perform_orca_reconcile step function. ex: `arn:aws:states:us-west-2:000000000000:stateMachine:PREFIX-OrcaInternalReconciliationWorkflow`
   5. `orca_INTERNAL_REPORT_SQS_URL` URL of the internal_report SQS queue. ex:`https://sqs.us-west-2.amazonaws.com/000000000000/PREFIX-orca-internal-report-queue.fifo`
   6. `orca_RECOVERY_BUCKET_NAME` S3 bucket name where the recovered files will be archived. ex: `test-orca-primary`
   7. `orca_REPORTS_BUCKET_NAME` S3 bucket name of the ORCA reports bucket. ex: `test-orca-reports`
   8. `orca_BUCKETS`The list of ORCA buckets used. ex: 
   ```json
   '{"protected": {"name": "'$PREFIX'-protected", "type": "protected"}, "internal": {"name": "'$PREFIX'-internal", "type": "internal"}, "private": {"name": "'$PREFIX'-private", "type": "private"}, "public": {"name": "'$PREFIX'-public", "type": "public"}, "orca_default": {"name": "'$PREFIX'-orca-primary", "type": "orca"}, "provider": {"name": "orca-sandbox-s3-provider", "type": "provider"}}'
   ```
   

4. 
   Get your Cumulus EC2 instance ID using the following AWS CLI command using your `<PREFIX>`.
   ```shell
   aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values={PREFIX}-CumulusECSCluster --query "Reservations[*].Instances[*].InstanceId" --output text
   ```
   Then run the following bash command, 
   replacing `i-00000000000000000` with your `PREFIX-CumulusECSCluster` ec2 instance ID, 
   and `0000000000.execute-api.us-west-2.amazonaws.com` with your API Gateway identifier:

   ```shell
   aws ssm start-session --target i-00000000000000000 --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters '{"host":["0000000000.execute-api.us-west-2.amazonaws.com"],"portNumber":["443"], "localPortNumber":["8000"]}'
   ```
5. In the root folder `workflow_tests`, run the following command:
   ```shell
   bin/run_tests.sh
   ```