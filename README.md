## Build lambdas
Before you can deploy this infrastructure, the lambda function source-code must be built.

`./build_tasks.sh` will crawl the `tasks` directory and build a `task.zip` (currently by just `zipping` all python files) in each of it's sub-directories. That `task.zip` is then referenced in the `app.tf` lamdba definitions.

## Setting up the Terraform deployment

### Variables
First, run a `mv terraform.tfvars.example terraform.tfvars` to get a template `terraform.tfvars` in your working directory. This is where you will place input variables to Terraform.

**Necessary:**
* ngap_subnet - NGAP Subnet
* ngap_sgs - NGAP Security Groups
* archive_bucket - Bucket with Glacier policy
* public_bucket - Bucket with public permissions (Cumulus public bucket)
* private_bucket - Bucket with private permissions (Cumulus private bucket)
* internal_bucket - Analogous to the Cumulus internal bucket 
* protected_bucket - Analogous to the Cumulus protected bucket
* permissions_boundary_arn - Permission Boundary Arn (Policy) for NGAP compliance

**Optional:**
* profile - AWS CLI Profile (configured via `aws configure`) to use. Defaults to `default`.
* region - Your AWS region. Defaults to `us-west-2`
* restore_expire_days - How many days to restore a file for. Defaults to 5.
* restore_request_retries - How many times to retry a restore request to Glacier. Defaults to 3.
* restore_retry_sleep_secs - How many seconds to wait between retry calls to `restore_object`. Defaults to 3.

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