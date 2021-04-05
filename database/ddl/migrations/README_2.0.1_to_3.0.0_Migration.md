# Installing ORCA with Cumulus Without Using the Release

1. Clone the ORCA repository and pull the latest updates of the branch you wish to test.
   ```
   git clone https://github.com/nasa/cumulus-orca.git
   cd cumulus-orca
   git checkout develop
   ```

2. Modify the following files in your Cumulus cumulus-tf deployment.
   - `orca.tf` -  Update the file to have the new required variables as seen below. Make sure to point the source to the proper cumulus-orca location and branch.
     ```
     module "orca" {
       source = "../../cumulus-orca/modules"
       ## --------------------------
       ## Cumulus Variables
       ## --------------------------
       ## REQUIRED
       aws_profile              = var.aws_profile
       buckets                  = var.buckets
       lambda_subnet_ids        = var.lambda_subnet_ids
       permissions_boundary_arn = var.permissions_boundary_arn
       prefix                   = var.prefix
       system_bucket            = var.system_bucket
       vpc_id                   = var.vpc_id
       workflow_config          = module.cumulus.workflow_config
     
       ## OPTIONAL
       region = var.region
       tags   = var.tags
     
       ## --------------------------
       ## ORCA Variables
       ## --------------------------
       ## REQUIRED
       database_app_user_pw = var.database_app_user_pw
       orca_default_bucket  = var.orca_default_bucket
       postgres_user_pw     = var.database_app_user_pw
     
       ## OPTIONAL
       # database_port                        = 5432
       # orca_ingest_lambda_memory_size       = 2240
       # orca_ingest_lambda_timeout           = 600
       # orca_recovery_buckets                = []
       # orca_recovery_complete_filter_prefix = ""
       # orca_recovery_expiration_days        = 5
       # orca_recovery_lambda_memory_size     = 128
       # orca_recovery_lambda_timeout         = 300
       # orca_recovery_retry_limit            = 3
       # orca_recovery_retry_interval         = 1
     ```
   - `variables.tf` or `orca_variables.tf` - Add the new required `orca_default_bucket` to the proper file.
     ```
     variable "orca_default_bucket" {
       type        = string
       description = "Default ORCA S3 Glacier bucket to use."
     }
     ```
   - `terraform.tfvars` - Add the new required `orca_default_bucket` variable and value. Update the buckets variable changing the type for the ORCA glacier bucket to *orca*.
     ```
     buckets = {
       internal = ....,
       glacier = {
         name = "my-orca-bucket",
         type = "orca"
       }
     }

     ...

     orca_default_bucket = "my-orca-bucket"
     ```


3. Run the terraform commands to deploy the changes. Verify that the ORCA components are added or updated in place.
   ```
   terraform init -rconfigure
   terraform plan
   terraform apply
   ```

4. Connect to the ORCA Postgres RDS database and manually run the migration SQL file. Note that you may need to add a rule to the security group to allow SSM access. The migration file is [here](001_migraton_2.0.1_to_3.0.0.sql).
   ```
   # In Window 1
   aws ssm start-session --target <Your EC2 instance> --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868

   # In Window 2
   ssh -p 6868 -N -L 5432:<Your PostgreSQL Host URL>:5432 -i <Your PEM Key> -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1

   # In Window 3
   # Run the file in your PostgreSQL client of choice
   ```

*NOTE:* Back end work is still ongoing. The tables will need to be filled with
Dummy data to validate status testing with the Cumulus Endpoints.

