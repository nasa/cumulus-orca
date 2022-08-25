#!/bin/bash
set -ex

cd integration_test

#initialize terraform
terraform init -input=false
#destroy using terraform
echo "Destroying DR S3 buckets in Disaster Recovery account"
terraform destroy \
  -auto-approve \
  -input=false