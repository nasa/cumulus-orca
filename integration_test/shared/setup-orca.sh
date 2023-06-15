#!/bin/bash
# Sets up TF files in a consistent manner.
set -ex
cwd=$(pwd)

export AWS_ACCESS_KEY_ID=$bamboo_CUMULUS_AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$bamboo_CUMULUS_AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$bamboo_CUMULUS_AWS_DEFAULT_REGION
export orca_API_DEPLOYMENT_INVOKE_URL=$bamboo_ORCA_API_DEPLOYMENT_INVOKE_URL
export orca_RECOVERY_STEP_FUNCTION_ARN=$bamboo_ORCA_RECOVERY_STEP_FUNCTION_ARN
export orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN=$bamboo_ORCA_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN
export orca_RECOVERY_BUCKET_NAME=$bamboo_ORCA_RECOVERY_BUCKET_NAME
# buckets structure tied to buckets.tf.template and dr-buckets.tf.template
export orca_BUCKETS='{"protected": {"name": "'$bamboo_PREFIX'-protected", "type": "protected"}, "internal": {"name": "'$bamboo_PREFIX'-internal", "type": "internal"}, "private": {"name": "'$bamboo_PREFIX'-private", "type": "private"}, "public": {"name": "'$bamboo_PREFIX'-public", "type": "public"}, "orca_default": {"name": "'$bamboo_PREFIX'-orca-primary", "type": "orca"}}'

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

    aws dynamodb create-table \
      --table-name ${bamboo_PREFIX}-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region ${bamboo_AWS_DEFAULT_REGION}
fi

git clone --branch ${bamboo_BRANCH_NAME} --single-branch https://github.com/nasa/cumulus-orca.git
echo "Cloned Orca, branch ${bamboo_BRANCH_NAME}"

cd integration_test
#replace prefix with bamboo prefix variable
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g' buckets.tf.template > buckets.tf

#configuring S3 backend
echo "terraform {
  backend \"s3\" {
    bucket = \"${bamboo_PREFIX}-tf-state\"
    region = \"${bamboo_AWS_DEFAULT_REGION}\"
    key    = \"terraform.tfstate\"
    dynamodb_table = \"${bamboo_PREFIX}-tf-locks\"
  }
}" >> terraform.tf
terraform init -input=false

#clone cumulus orca template for deploying RDS cluster
cd ..
git clone --branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION --single-branch https://git.earthdata.nasa.gov/scm/orca/cumulus-orca-deploy-template.git
echo "cloned Cumulus, branch $bamboo_CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION"

#rds-cluster-tf module
cd cumulus-orca-deploy-template/rds-cluster-tf
echo "inside rds-cluster-tf"
mv terraform.tfvars.example terraform.tfvars

#replacing terraform.tf and environment variables with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
export VPC_ID=$(aws ec2 describe-vpcs | jq -r '.Vpcs | to_entries | .[] | .value.VpcId')
export AWS_SUBNET_ID1=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2a"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID2=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2b"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
export AWS_SUBNET_ID3=$(aws ec2 describe-subnets --filters "Name=availability-zone,Values=us-west-2c"| jq -r '.Subnets | .[] | select (.Tags | .[] | .Value | contains ("Private application ")) | .SubnetId ')
terraform init -input=false

#data persistence tf module
cd ../data-persistence-tf
mv terraform.tfvars.example terraform.tfvars
#replacing terraform.tf with proper values
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf
terraform init -input=false

cd ../cumulus-tf
#replacing .tf files with proper values
sed 's/PREFIX/'"$bamboo_PREFIX"'/g' terraform.tfvars.example > terraform.tfvars
sed -e 's/PREFIX/'"$bamboo_PREFIX"'/g; s/us-east-1/'"$bamboo_AWS_DEFAULT_REGION"'/g' terraform.tf.example > terraform.tf
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