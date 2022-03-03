---
id: research-bamboo-integration-tests
title: Research Notes on running integration tests in bamboo CI/CD
description: Research Notes on deploying Cumulus and ORCA in bamboo CI/CD and running integration tests.
---

## Deploying terraform modules via bamboo
AWS resources can be deployed via Bamboo pipeline by first adding the following to a script and running that in a Bamboo task.

```bash
#configure aws 
aws configure set aws_access_key_id $bamboo_AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $bamboo_AWS_SECRET_ACCESS_KEY
aws configure set default.region $bamboo_AWS_DEFAULT_REGION
```

:::note
In order to use a user-defined bamboo environment variable inside a script, `$bamboo_` must be added as a prefix to the variable. For example, use `$bamboo_AWS_DEFAULT_REGION` in your script to use the variable AWS_DEFAULT_REGION.
:::

Details of some of the initial work done are added in the [ORCA-test-bamboo](https://github.com/nasa/cumulus-orca/tree/feature/ORCA-test-bamboo) branch of `cumulus-orca` repo.
The [bamboo spec file](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bamboo-specs/bamboo.yaml#L22) has been modified to add two new stages named `Deploy Dev RDS Stack` stage which deploys the RDS cluster in sandbox and the `Deploy Dev Cumulus and ORCA Stack` stage which deploys the data persistence module as well as cumulus and orca modules. The stages in bamboo spec are shown below.
```yaml
#deploy RDS cluster for integration test
- Deploy Dev RDS Stack:
    manual: true
    final: false
    jobs:
    - Deploy RDS cluster

#deploy orca and cumulus for integration test
- Deploy Dev Cumulus and ORCA Stack:
    manual: true
    final: false
    jobs:
    - Deploy cumulus and orca
```
The [`deployment-rds.sh`](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bin/deployment-rds.sh) script is an initial working script that was used to deploy the RDS cluster. The [`deployment-cumulus-orca.sh`](https://github.com/nasa/cumulus-orca/blob/feature/ORCA-test-bamboo/bin/deployment-cumulus-orca.sh) script was used to deploy the data-persistence-tf module. Some changes still need to be made in these scripts to make it more functional and handle errors. A successful bamboo build can be seen [here](https://ci.earthdata.nasa.gov/browse/ORCA-PP-108).
A snippet of the script to deploy RDS cluster via terraform is shown below.
```bash
# Deploy drds-cluster-tf via terraform
echo "Deploying rds-cluster-tf  module to $bamboo_DEPLOYMENT"
terraform apply \
  -auto-approve \
  -lock=false \
  -input=false \
  -var-file="terraform.tfvars" \
  -var "prefix=$bamboo_PREFIX" \
  -var "region=$bamboo_AWS_DEFAULT_REGION" \
  -var "subnets=[\"$bamboo_AWS_SUBNET_ID1\", \"$bamboo_AWS_SUBNET_ID2\"]" \
  -var "db_admin_username=$bamboo_DB_ADMIN_USERNAME" \
  -var "db_admin_password=$bamboo_DB_ADMIN_PASSWORD" \
  -var "vpc_id=$bamboo_VPC_ID" \
  -var "cluster_identifier=$bamboo_RDS_CLUSTER_ID" \
  -var "deletion_protection=false"\
  -var "provision_user_database=false"\
  -var "engine_version=10.14"\
  -var "permissions_boundary_arn=arn:aws:iam::$bamboo_AWS_ACCOUNT_ID:policy/$bamboo_ROLE_BOUNDARY"
```
Variables in terraform.tfvars can be overwritten by the `-var` field as seen above. 

Some of the sensitive bamboo variables such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `RDS_USER_ACCESS_SECRET_ARN` have been encrypted using bamboo encryption service. While running the pipeline, those variables have to be replaced manually with the real values since bamboo does not automatically decrypt the values while running the pipeline. Make sure all sensitive variables are encrypted before pushing the changes to the repo. 

The bamboo spec for running the two scripts under tasks is shown below.

```yaml
#job for deploying cumulus and orca
Deploy RDS cluster:
  key: DRC
  other:
    clean-working-dir: true
    # Some plugin configurations are not supported by YAML Specs
  docker:
    image: amazonlinux:2
    volumes:
      ${bamboo.working.directory}: ${bamboo.working.directory}
      ${bamboo.tmp.directory}: ${bamboo.tmp.directory}
  tasks:
  - checkout:
      force-clean-build: 'true'
      description: Checkout Default Repository

  - script:
      interpreter: SHELL
      scripts:
      - |-
        #!/bin/bash
        chmod +x bin/deployment-rds.sh
        bin/deployment-rds.sh
#job for deploying cumulus and orca
Deploy cumulus and orca:
  key: DCO
  other:
    clean-working-dir: true
    # Some plugin configurations are not supported by YAML Specs
  docker:
    image: amazonlinux:2
    volumes:
      ${bamboo.working.directory}: ${bamboo.working.directory}
      ${bamboo.tmp.directory}: ${bamboo.tmp.directory}
  tasks:
  - checkout:
      force-clean-build: 'true'
      description: Checkout Default Repository

  - script:
      interpreter: SHELL
      scripts:
      - |-
        #!/bin/bash
        chmod +x bin/deployment-cumulus-orca.sh
        bin/deployment-cumulus-orca.sh
```

## Future directions

The first step will be to finish deploying all cumulus tf modules via Bamboo into sandbox account. Once that is completed, automation scripts for running the integrations tests need to be created. The original plan `ORCA Integrator` in bamboo will need to be updated with the same changes made in `prototype-demo` plan's `feature/ORCA-test-bamboo` branch so that the `develop` branch is updated. In addition, older resources should be deleted from AWS once tests are validated. 
Some of the cards created to finish the task include:
- https://bugs.earthdata.nasa.gov/browse/ORCA-388
- https://bugs.earthdata.nasa.gov/browse/ORCA-389
- https://bugs.earthdata.nasa.gov/browse/ORCA-390
- https://bugs.earthdata.nasa.gov/browse/ORCA-391
- https://bugs.earthdata.nasa.gov/browse/ORCA-392
- https://bugs.earthdata.nasa.gov/browse/ORCA-393


##### References
- https://github.com/nasa/cumulus/tree/master/bamboo
- Slack communication in cumulus-internal channel