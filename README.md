## Build lambdas
Before you can deploy this infrastructure, the lambda function source-code must be built.

`./bin/build_tasks.sh` will crawl the `tasks` directory and build a `task.zip` (currently by just `zipping` all python files) in each of it's sub-directories. That `task.zip` is then referenced in the `app.tf` lamdba definitions.

## Setting up the Terraform deployment

### Variables
First, run a `mv terraform.tfvars.example terraform.tfvars` to get a template `terraform.tfvars` in your working directory. This is where you will place input variables to Terraform.

**Necessary:**
* ngap_subnet - NGAP Subnet
* ngap_sgs - NGAP Security Groups
* glacier_bucket - Bucket with Glacier policy
* public_bucket - Bucket with public permissions (Cumulus public bucket)
* private_bucket - Bucket with private permissions (Cumulus private bucket)
* internal_bucket - Analogous to the Cumulus internal bucket 
* protected_bucket - Analogous to the Cumulus protected bucket
* permissions_boundary_arn - Permission Boundary Arn (Policy) for NGAP compliance

**Optional:**
* prefix - Prefix that will be pre-pended to resource names created by terraform. Defaults to `dr`.
* profile - AWS CLI Profile (configured via `aws configure`) to use. Defaults to `default`.
* region - Your AWS region. Defaults to `us-west-2`
* restore_expire_days - How many days to restore a file for. Defaults to 5.
* restore_request_retries - How many times to retry a restore request to Glacier. Defaults to 3.
* restore_retry_sleep_secs - How many seconds to wait between retry calls to `restore_object`. Defaults to 3.
* copy_retries - How many times to retry a copy request from the restore location to the archive location. Defaults to 3.
* copy_retry_sleep_secs - How many seconds to wait between retry calls to `copy_object`. Defaults to 0.
* copy_bucket_map - Stringified JSON object mapping file extensions to `Public` or `Private` buckets.

## Deploying with Terraform
Visit the [Terraform documentation](https://learn.hashicorp.com/terraform/getting-started/install.html) for installation instructions.

```
terraform init
terraform plan #optional, but allows you to preview the deploy
terraform apply
```

## Delete Terraform stack
```
terraform destroy
```

## External Terraform State
By default, Terraform stores your deployment state locally. This may not be desirable as if another developer/user will be unable to make changes to your deployment without first receiving your state file.

The following will be an example of how to keep your terraform state in an S3 bucket with access protection/file locking with dynamodb:

Create a bucket where your tfstate file will be stored (and enable versioning)
```
$ aws s3api create-bucket \
    --bucket "${state-bucket}"
    --create-bucket-configuration LocationConstraint=us-west-2
$ aws s3api put-bucket-versioning \
    --bucket "${state-bucket}" \
    --versioning-configuration Status=Enabled
```
**Note:** The `--create-bucket-configuration` line is only necessary if you are creating your bucket outside of `us-east-1`.

Create the dynamodb table that will be used for locking
```
$ aws dynamodb create-table \
    --table-name "${state-table-name}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```
**Note:** If the above `create-table` command yells about some missing parameter, try updating your awscli tool.

Add the following in a file as `terraform.tf` (in the same directory as your other `.tf` files)
```
terraform {
  backend "s3" {
    region         = "us-west-2"
    bucket         = "podaac-dr-tf-state"
    key            = "terraform.tfstate"
    dynamodb_table = "podaac-dr-tf-locks"
  }
}
```