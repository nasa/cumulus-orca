#!/bin/bash
set -ex

cd integration_test

#deploy using terraform
echo "Deploying DR S3 buckets in Disaster Recovery account"
terraform apply \
  -auto-approve \
  -input=false
