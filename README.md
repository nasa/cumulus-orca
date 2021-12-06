## ORCA Static Documentation

ORCA documentation can be found at [nasa.github.io/cumulus-orca](https://nasa.github.io/cumulus-orca). 
The documentation is available for developers, data managers, and users.
Additional documentation is being added continually.

Make sure you are using the following node.js versions to view the documentation.
- npm 6.14.10
- node 12.15.0

Further ORCA documentation can be read locally by performing the following:
```
cd website
npm install
npm run start
```

Once the server is running, documentation should be available on `http://localhost:3000`.

## Clone and build Operational Recovery Cloud Archive (ORCA)

Clone the `dr-podaac-swot` repo from https://github.com/ghrcdaac/operational-recovery-cloud-archive

```
git clone https://github.com/ghrcdaac/operational-recovery-cloud-archive
```
## Build lambdas
Before you can deploy this infrastructure, you must download the release zip, or the build the lambda function source-code locally.

`./bin/build_tasks.sh` will crawl the `tasks` directory and build a `.zip` file (currently by just `zipping` all python files and dependencies) in each of it's sub-directories. That `.zip` is then referenced in the `modules/lambdas/main.tf` lambda definitions.

```
./bin/build_tasks.sh
```

# ORCA Deployment

The ORCA deployment is done with [Terraform root module](https://www.terraform.io/docs/configuration/modules.html),
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

These steps should be executed in the root directory of the repo.

Create a `terraform.tf` file, substituting the appropriate values for `bucket`
and `dynamodb_table`. This tells Terraform where to store its
remote state.

**terraform.tf**

```
terraform {
  backend "s3" {
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
* `buckets` - AWS S3 bucket mapping used for Cumulus and ORCA configuration.
* `permissions_boundary_arn` - Permission Boundary Arn (Policy) for NGAP compliance
* `db_admin_password` - Password for RDS database administrator authentication
* `db_user_password` - Password for RDS database user authentication
* `db_host_endpoint` - Database host endpoint to connect to.

**Optional:**
* `db_admin_username` -  Username for RDS database administrator authentication.
* `prefix` - Prefix that will be pre-pended to resource names created by terraform. 
  Defaults to `dr`.
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
* `drop_database` - Whether to drop the database if it exists (True), or keep it (False). 
  Defaults to False.
* `database_port` - the port for the postgres database. 
  Defaults to '5432'.
* `platform` - indicates if running locally (onprem) or in AWS (AWS). 
  Defaults to 'AWS'.

## Deploying with Terraform
Run `terraform init`.
Run `terraform plan` #optional, but allows you to preview the deploy.
Run `terraform apply`.

This will deploy ORCA.

## Delete Terraform stack
If you want to remove it:
```
terraform destroy
```

## Integrating with Cumulus
Integrate ORCA with Cumulus to be able to recover a granule from the Cumulus Dashboard.

### Define the ORCA workflow (Cumulus < v1.15)

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
}
```

### Integrating ORCA With Cumulus >= v1.15

#### Adding a ORCA module to the Cumulus deployment

Navigate to `cumulus-tf/main.tf` within your Cumulus deployment directory and add the following module:
```
module "orca" {
  source = "https://github.com/ghrcdaac/operational-recovery-cloud-archive/releases/download/1.0.2/orca-1.0.2.zip"
  
  ## --------------------------
  ## Cumulus Variables
  ## --------------------------
  ## REQUIRED
  buckets                  = var.buckets
  lambda_subnet_ids        = var.lambda_subnet_ids
  permissions_boundary_arn = var.permissions_boundary_arn
  buckets = var.buckets
  workflow_config = module.cumulus.workflow_config
  default_multipart_chunksize_mb = module.cumulus.default_multipart_chunksize_mb
}

```

*Note*: This above snippet assumes that you've configured your Cumulus deployment. More information on that process can be found in their [documentation](https://nasa.github.io/cumulus/docs/deployment/deployment-readme#configure-and-deploy-the-cumulus-tf-root-module)

#### Add necessary variables (unique to ORCA) to the Cumulus TF configuration

To support this module, you'll have to add the following values to your `cumulus-tf/variables.tf` file:
```
# Variables specific to ORCA

variable "db_admin_username" {
  type = string
  description = "Username for RDS database administrator authentication"
}

variable "db_admin_password" {
  type = string
  description = "Password for RDS database administrator authentication"
}

variable "db_user_password" {
  type = string
  description = "Password for RDS database user authentication"
}
```

The values corresponding to these variables must be set in your `cumulus-tf/terraform.tfvars` file, but note that many of these variables are actually hardcoded at the time of updating this README

#### Adding the Copy To Glacier Step to the Ingest Workflow
Navigate to `cumulus-tf/ingest_granule_workflow.tf` then add the following
step to anywhere after the MoveGranule step being sure to change the 
"Next" parameter equal to "CopyToGlacier".
```
"CopyToGlacier":{
         "Parameters":{
            "cma":{
               "event.$":"$",
               "task_config":{
                  "bucket":"{$.meta.buckets.internal.name}",
                  "buckets":"{$.meta.buckets}",
                  "distribution_endpoint":"{$.meta.distribution_endpoint}",
                  "files_config":"{$.meta.collection.files}",
                  "multipart_chunksize_mb": "{$.meta.collection.multipart_chunksize_mb"},
                  "orcaDefaultBucketOverride": "{$.meta.collection.meta.orca_default_bucket}"
                  "fileStagingDir":"{$.meta.collection.url_path}",
                  "granuleIdExtraction":"{$.meta.collection.granuleIdExtraction}",
                  "collection":"{$.meta.collection}",
                  "cumulus_message":{
                     "input":"{[$.payload.granules[*].files[*].filename]}",
                     "outputs":[
                        {
                           "source":"{$}",
                           "destination":"{$.payload}"
                        }
                     ]
                  }
               }
            }
         },
         "Type":"Task",
         "Resource":"${module.orca.copy_to_glacier_lambda_arn}",
         "Catch":[
            {
               "ErrorEquals":[
                  "States.ALL"
               ],
               "ResultPath":"$.exception",
               "Next":"WorkflowFailed"
            }
         ],
         "Retry":[
            {
               "ErrorEquals":[
                  "States.ALL"
               ],
               "IntervalSeconds":2,
               "MaxAttempts":3
            }
         ],
         "Next":"WorkflowSucceeded"
      },
```

### Collection configuration
To configure a collection to enable ORCA, add the line
`"granuleRecoveryWorkflow": "DrRecoveryWorkflow"` to the collection configuration:
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
    "granuleRecoveryWorkflow": "DrRecoveryWorkflow"
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

## Release Documentation:

Information about how to create an ORCA release can be found [here](docs/release.md).
