#!/bin/bash
# Sets up TF files in a consistent manner.
set -ex
cwd=$(pwd)

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

#remove old files from bamboo as they throw error
rm *.tf

if aws s3api head-bucket --bucket ${bamboo_PREFIX}-tf-state;then
    echo "terraform state bucket already present. Using existing state file"
else
    echo "Something went wrong when checking terraform state bucket. Creating ..."
    aws s3api create-bucket --bucket ${bamboo_PREFIX}-tf-state  --region ${bamboo_AWS_DEFAULT_REGION} --create-bucket-configuration LocationConstraint=${bamboo_AWS_DEFAULT_REGION}
    
    aws s3api put-bucket-versioning \
    --bucket ${bamboo_PREFIX}-tf-state \
    --versioning-configuration Status=Enabled

    echo "Deploying dynamoDB table"
    aws dynamodb create-table \
      --table-name ${bamboo_PREFIX}-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region ${bamboo_AWS_DEFAULT_REGION}
fi

git clone --branch ${bamboo_BRANCH_NAME} --single-branch https://github.com/nasa/cumulus-orca.git
echo "Cloned Orca, branch ${bamboo_BRANCH_NAME}"

# Init ORCA
cd cumulus-orca
echo "inside orca"
#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"${bamboo_PREFIX}/orca/terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf
terraform init -input=false
#cd ..

# todo: integration_test folder exists at root AND in cumulus-orca. Just use one. https://bugs.earthdata.nasa.gov/browse/ORCA-708
cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"${bamboo_PREFIX}/buckets/terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf
terraform init -input=false

#clone cumulus orca template for deploying RDS cluster
cd ..
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
echo "cloned Cumulus, branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION"

#rds-cluster-tf module
rds_path="cumulus-orca-deploy-template/terraform-aws-cumulus/tf-modules/cumulus-rds-tf"
cd "$rds_path"
echo "inside $rds_path"
#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"${bamboo_PREFIX}/rds/terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf
terraform init -input=false
cd ../../../..

# ecs-standalone module
ecs_path="cumulus-orca-deploy-template/ecs-standalone-tf"
cd "$ecs_path"
echo "inside $ecs_path"
#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"${bamboo_PREFIX}/ecs/terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf
terraform init -input=false
cd ../..

# Remove all prevent_destroy properties
for f in $(find cumulus-orca-deploy-template -name '*.tf');
do
    echo "Removing prevent_destroy from $f ..."
    sed 's/prevent_destroy = true/prevent_destroy = false/g' $f > temp
    mv temp $f
done;

cd "${cwd}"
