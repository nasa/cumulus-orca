#!/bin/bash
set -ex
cwd=$(pwd)

#rds_endpoint=$(aws rds describe-db-cluster-endpoints --db-cluster-identifier $bamboo_PREFIX-cumulus-rds-serverless-default-cluster --query 'DBClusterEndpoints[].Endpoint | [0]' --output text)
ec2_instance_id=$(aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values=${bamboo_PREFIX}-CumulusECSCluster --query "Reservations[*].Instances[*].InstanceId" --output text)
api_gateway_id=$(aws apigateway get-rest-apis --query "items[?name==\`${bamboo_PREFIX}_orca_api\`].id | [0]")
#  --output text is bugged for get-rest-apis. Have to manually remove the "" around the result to keep variable formatting consistent.
api_gateway_id="${api_gateway_id:1:${#api_gateway_id}-2}"

export orca_API_DEPLOYMENT_INVOKE_URL="${api_gateway_id}.execute-api.${bamboo_CUMULUS_AWS_DEFAULT_REGION}.amazonaws.com"

(aws ssm start-session --target $ec2_instance_id --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters "{\"host\":[\"${orca_API_DEPLOYMENT_INVOKE_URL}\"],\"portNumber\":[\"443\"], \"localPortNumber\":[\"8000\"]}") &
#(ssh -p 6868 -L 5432:$rds_endpoint:5432 -i "../../EC2KeyPair.pem" -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1) &
sleep 5
#(aws ssm start-session --target $ec2_instance_id --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868) &
#sleep 5

cd "${cwd}"