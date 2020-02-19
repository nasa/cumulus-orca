## Clone and build Disaster Recovery

Clone the `dr-podaac-swot` repo from <https://git.earthdata.nasa.gov/scm/pocumulus/dr-podaac-swot.git>

```
git clone https://git.earthdata.nasa.gov/scm/pocumulus/dr-podaac-swot.git disaster-recovery
```
## Build lambdas
Before you can deploy this infrastructure, the lambda function source-code must be built.

`./bin/build_tasks.sh` will crawl the `tasks` directory and build a `.zip` file (currently by just `zipping` all python files and dependencies) in each of it's sub-directories. That `.zip` is then referenced in the `main.tf` lamdba definitions.

```
cd disaster-recovery
./bin/build_tasks.sh
```

# Disaster Recovery Deployment

The Disaster Recovery deployment is done with [Terraform root module](https://www.terraform.io/docs/configuration/modules.html),
`main.tf`.

The following instructions will walk you through installing Terraform,
configuring Terraform, and deploying the root module.

## Install Terraform

If you are using a Mac and [Homebrew](https://brew.sh), installing Terraform is
as simple as:

```shell
brew update
brew install terraform
```

For other cases,
Visit the [Terraform documentation](https://learn.hashicorp.com/terraform/getting-started/install.html) for installation instructions.

Verify that the version of Terraform installed is at least v0.12.0.

```shell
$ terraform --version
Terraform v0.12.2
```

## Configure the Terraform backend

The state of the Terraform deployment is stored in S3. In the following
examples, it will be assumed that state is being stored in a bucket called
`dr-tf-state`. You can also use an existing bucket, if desired.

Create the state bucket:

```shell
aws s3api create-bucket --bucket dr-tf-state --create-bucket-configuration LocationConstraint=us-west-2
```
**Note:** The `--create-bucket-configuration` line is only necessary if you are creating your bucket outside of `us-east-1`.

In order to help prevent loss of state information, it is recommended that
versioning be enabled on the state bucket:

```shell
$ aws s3api put-bucket-versioning \
    --bucket dr-tf-state \
    --versioning-configuration Status=Enabled
```

Terraform uses a lock stored in DynamoDB in order to prevent multiple
simultaneous updates. In the following examples, that table will be called
`dr-tf-locks`.

Create the locks table:

⚠️ **Note:** The `--billing-mode` option was recently added to the AWS CLI. You
may need to upgrade your version of the AWS CLI if you get an error about
provisioned throughput when creating the table.

```shell
$ aws dynamodb create-table \
    --table-name dr-tf-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## Configure and deploy the `main` root module

These steps should be executed in the `disaster-recovery` directory.

Create a `terraform.tf` file, substituting the appropriate values for `bucket`
and `dynamodb_table`. This tells Terraform where to store its
remote state.

**terraform.tf**

```
terraform {
  backend "s3" {
    region         = "us-west-2"
    bucket         = "dr-tf-state"
    key            = "terraform.tfstate"
    dynamodb_table = "dr-tf-locks"
  }
}
```
## Variables
First, run a `mv terraform.tfvars.example terraform.tfvars` to get a template `terraform.tfvars` in your working directory. This is where you will place input variables to Terraform.

**Necessary:**
* `ngap_subnets` - NGAP Subnets (array)
* `vpc_id` - ID of VPC to place resources in - recommended that this be a private VPC (or at least one with restricted access).
* `glacier_bucket` - Bucket with Glacier policy
* `public_bucket` - Bucket with public permissions (Cumulus public bucket)
* `private_bucket` - Bucket with private permissions (Cumulus private bucket)
* `internal_bucket` - Analogous to the Cumulus internal bucket 
* `protected_bucket` - Analogous to the Cumulus protected bucket
* `permissions_boundary_arn` - Permission Boundary Arn (Policy) for NGAP compliance
* `postgres_user_pw` - password for the postgres user
* `database_name` - disaster_recovery
* `database_app_user` - druser 
* `database_app_user_pw` - the password for the application user

**Optional:**
* `prefix` - Prefix that will be pre-pended to resource names created by terraform. 
  Defaults to `dr`.
* `profile` - AWS CLI Profile (configured via `aws configure`) to use. 
  Defaults to `default`.
* `region` - Your AWS region. 
  Defaults to `us-west-2`.
* `restore_expire_days` - How many days to restore a file for. 
  Defaults to 5.
* `restore_request_retries` - How many times to retry a restore request to Glacier. 
  Defaults to 3.
* `restore_retry_sleep_secs` - How many seconds to wait between retry calls to `restore_object`. 
  Defaults to 3.
* `restore_retrieval_type` -  the Tier for the restore request. Valid values are 'Standard'|'Bulk'|'Expedited'. 
  Defaults to `Standard`. Understand the costs associated with the tiers before modifying.
* `copy_retries` - How many times to retry a copy request from the restore location to the archive location. 
  Defaults to 3.
* `copy_retry_sleep_secs` - How many seconds to wait between retry calls to `copy_object`. 
  Defaults to 0.
* `ddl_dir` - the location of the ddl dir that contains the sql to create the application database. 
  Defaults to 'ddl/'.
* `drop_database` - Whether or not to drop the database if it exists (True), or keep it (False). 
  Defaults to False.
* `database_port` - the port for the postgres database. 
  Defaults to '5432'.
* `platform` - indicates if running locally (onprem) or in AWS (AWS). 
  Defaults to 'AWS'.

## Deploying with Terraform
Run `terraform init`.
Run `terraform plan` #optional, but allows you to preview the deploy.
Run `terraform apply`.

This will deploy Disaster Recovery.

## Delete Terraform stack
If you want to remove it:
```
terraform destroy
```

## Integrating with Cumulus
Integrate Disaster Recovery with Cumulus to be able to recover a granule from the Cumulus Dashboard.

### Define the Disaster Recovery workflow (Cumulus < v1.15)

Copy the workflow from `workflows/workflows.yml.dr` into your Cumulus workflow.

Set the values of these environment variables to the ARN for the 
{prefix}-extract-filepaths-for-granule and {prefix}-request-files lambdas,
respectively:
```
DR_EXTRACT_LAMBDA_ARN=arn:aws:lambda:us-west-2:012345678912:function:dr_extract_filepaths_for_granule

DR_REQUEST_LAMBDA_ARN=arn:aws:lambda:us-west-2:012345678912:function:dr_request_files
```

Add an `aws` provider to `main.tf`:

```
provider "aws" {
  version = "~> 2.13"
  region  = var.region
  profile = var.profile
}
```

### Integrating Disaster Recovery With Cumulus >= v1.15

#### Adding a DR module to the Cumulus deployment

We will be adding a `disaster-recovery` module to `cumulus-tf/main.tf`. First, since there isn't a distributed version of the `disaster-recovery` module at the time of writing this documentation, you'll have to clone this repository locally: `https://github.com/podaac/cumulus-disaster-recovery.git`.

In the `disaster-recovery` repo, build the lambda tasks with `./bin/build_tasks.sh`.

Once that is done, navigate to `cumulus-tf/main.tf` within your Cumulus deployment directory and add the following module:
```
module "disaster-recovery" {
  source = "<location of dr module locally>"

  prefix = var.prefix
  vpc_id = var.vpc_id

  ngap_subnets             = var.ngap_db_subnets
  public_bucket            = var.buckets["public"]["name"]
  glacier_bucket           = var.buckets["glacier"]["name"]
  private_bucket           = var.buckets["private"]["name"]
  internal_bucket          = var.buckets["internal"]["name"]
  protected_bucket         = var.buckets["protected"]["name"]
  permissions_boundary_arn = var.permissions_boundary_arn
  postgres_user_pw         = var.postgres_user_pw
  database_name            = var.dr_database_name
  database_app_user        = var.dr_database_app_user
  database_app_user_pw     = var.dr_database_app_user_pw
}
```

*Note*: This above snippet assumes that you've configured your Cumulus deployment. More information on that process can be found in their [documentation](https://nasa.github.io/cumulus/docs/deployment/deployment-readme#configure-and-deploy-the-cumulus-tf-root-module)

#### Add necessary variables (unique to DR) to the Cumulus TF configuration

To support this module, you'll have to add the following values to your `cumulus-tf/variables.tf` file:
```
# Variables specific to DR
variable "ngap_db_subnets" {
  type = list(string)
}

variable "postgres_user_pw" {
  type = string
}

variable "dr_database_name" {
  type = string
}

variable "dr_database_app_user" {
  type = string
}

variable "dr_database_app_user_pw" {
  type = string
}
```

The values corresponding to these variables must be set in your `cumulus-tf/terraform.tfvars` file.

#### Adding a recovery workflow

Copy the workflow from `workflows/dr_recovery_workflow.tf` into your `cumulus-tf/` directory. In the workflow file you may need to change the `disaster-recovery` portion of the following two strings to the name of your disaster-recovery module (defined in `cumulus-tf/main.tf`):

1. `module.disaster-recovery.extract_filepaths_lambda_arn`
2. `module.disaster-recovery.request_files_lambda_arn`

### Collection configuration
To configure a collection to enable Disaster Recovery, add the line
`"granuleRecoveryWorkflow": DrRecoveryWorkflow"` to the collection configuration:
```
{
  "queriedAt": "2019-11-07T22:49:46.842Z",
  "name": "L0A_HR_RAW",
  "version": "1",
  "sampleFileName": "L0A_HR_RAW_product_0001-of-0420.h5",
  "dataType": "L0A_HR_RAW",
  "granuleIdExtraction": "^(.*)((\\.cmr\\.json)|(\\.iso\\.xml)|(\\.tar\\.gz)|(\\.h5)|(\\.h5\\.mp))$",
  "reportToEms": true,
  "createdAt": 1561749178492,
  "granuleId": "^.*$",
  "provider_path": "L0A_HR_RAW/",
  "meta": {
    "response-endpoint": "arn:aws:sns:us-west-2:012345678912:providerResponseSNS",
    "glacier-bucket": "podaac-sndbx-cumulus-glacier",
    "granuleRecoveryWorkflow": DrRecoveryWorkflow"
  },
  "files": [
    {
```
### Enable `Recover Granule` button

To enable the `Recover Granule` button on the Cumulus Dashboard (available at github.com/nasa/cumulus-dashboard), 
set the environment variable `ENABLE_RECOVERY=true`.

Here is an example command to run the Cumulus Dashboard locally:
```
  APIROOT=https://uttm5y1jcj.execute-api.us-west-2.amazonaws.com:8000/dev ENABLE_RECOVERY=true npm run serve
```
