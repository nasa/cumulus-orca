---
id: versioning-releases
title:  ORCA Versioning and Releases
description: Provides information to developers on semantic versioning and the release process.
---

Much of this documentation is also found at [Cumulus](https://github.com/nasa/cumulus/blob/master/docs/development/release.md).

## Versioning

The ORCA team uses semantic versioning. More information about semantic
versioning can be found [here](https://semver.org/).

## Release Process

### Create a release branch

From develop, create a new release branch from develop following the
`release-MAJOR.MINOR.x`. For example, `release-1.14.1`. Push this branch 
to github if you created it locally.

### Update CHANGELOG.md

Update the [CHANGELOG.md](https://github.com/nasa/cumulus-orca/blob/master/CHANGELOG.md). 
Put a header under the 'Unreleased' section with the new version number and 
the date.

### Create a git tag for the release

Make sure you're on the latest commit of the release branch.

Create and push a new git tag:

```
    git tag -a vx.y.z -m "Release x.y.z"
    git push origin vx.y.z
```

### Running the deployment

Publishing of new releases is handled by a Bamboo release plan and is manually
triggered.

If you created a new release branch in step one, you will need to create a new
bamboo deployment plan.

#### Creating a Bamboo deployment plan

1. The deployment plan is already created in Bamboo using [Bamboo Specs](https://github.com/nasa/cumulus-orca/tree/develop/bamboo-specs). If you have updated the `bamboo.yaml` config file, you will need to import the updated spec file from Bamboo specs UI. Under `Specs` section, click on the `Set up Specs Repository`. On the `Project Type`, select `Build Project` and then `ORCA`. On the Specs repository, select the repository host as `orca-develop`. Note that choosing the wrong repository branch will cause issues in deployment. `ORCA repo` repository host is for `master` branch and `orca test branch` host is for `feature/ORCA-test-bamboo` branch used for testing and prototyping. Contact `Venku Jayanti` from CI/CD team for additional support.
   In the ORCA project (https://ci.earthdata.nasa.gov/browse/ORCA-OI), scroll to the top left of the page where it indicates `Plan branch`. From the `Plan branch` dropdown menu, select the release branch you created for the release which should be in the format `release-X.X.X`.
2. Once inside the release branch page, scroll to the top right of the page and click `Actions`-> `Configure branch`.
3. On the `Plan branch configuration` page, under `Plan branch configuration`, enable 'Change Trigger'. Set the 
   Trigger type to manual, and this will prevent commits to the branch from triggering the build plan.
4. Click on the `Variables` tab.
Ensure that you are on your branch plan and not the master plan. Click on the `Choose from inherited variables` dropdown menu.
   except in special cases such as incompatible backport branches. Then add and set the following variables:
     * ORCA_VERSION: `<version number>`
     * RELEASE_FLAG: true
     * SECRET_GITHUB_EMAIL: `<secret github email>`
     * SECRET_GITHUB_TOKEN: `<secret github token>`
     * SECRET_GITHUB_USER: `<secret github user>`
   
   Contact ORCA team to know values of the three github variables.
5. Run the branch using the 'Run' button in the top right.

Bamboo will build and run unit tests against that tagged release.

## Create a new ORCA release on github

The release is automated in Bamboo, but the step must be manually started. If
you set the `RELEASE_FLAG` to `true` and the build steps passed, you will
be able to run the manual 'Release' step in Bamboo.

The CI release scripts will create a release based on the release version tag,
as well as uploading release artifacts to the Github release for the Terraform
modules provided by Cumulus. The Terraform release artifacts include:

* A multi-module Terraform .zip artifact containing filtered copies of the 
  tf-modules, packages, and tasks directories for use as Terraform module sources.

Just make sure to verify the appropriate .zip files are present on Github after
the release process is complete.

**Merge the base branch back into develop and master**

Finally, you need to merge the version update changes back into develop and 
master.

If this is the latest version, create the PRs to merge the release branch 
into develop and master. 

:::note Note: 

Do not squash this merge. Doing so will make the "compare" view from step 4 
show an incorrect diff, because the tag is linked to a specific commit on the 
base branch.

:::

## Troubleshooting

### Delete and regenerate the tag

To delete a published tag to re-tag, follow these steps:

```
    git tag -d vx.y.z
    git push -d origin vx.y.z
```

## Deploying RDS cluster and Cumulus ORCA modules in bamboo

For testing, use your feature branch in cumulus-orca github repo and `ORCA-test-branch` linked repo in bamboo specs. 

While running the `Deploy Dev RDS Stack` stage, replace the following variables with yours. This is because some variables are sensitive and some will vary depending upon the user running the pipeline. Hitting 'play' next to `Deploy Dev RDS Stack` and `Deploy Dev Cumulus and ORCA Stack` brings up a checkbox list to run multiple jobs at once. Note that none of the checkboxes should be checked.

- AWS_ACCESS_KEY_ID(for cumulus sandbox account)
- AWS_SECRET_ACCESS_KEY(for cumulus sandbox account)
- PREFIX
- AWS_ACCOUNT_ID(for cumulus sandbox account)
- DB_ADMIN_PASSWORD
- DB_USER_PASSWORD

The ORCA buckets and dynamoDB table are created automatically in bamboo `Deploy Dev Cumulus and ORCA Stack` stage. However, these can also be created manually if desired by the user. These are the buckets that need to be created:

- `<PREFIX>-internal`
- `<PREFIX>-level0`
- `<PREFIX>-public`
- `<PREFIX>-private`
- `<PREFIX>-protected`
- `<PREFIX>-orca-primary`
- `<PREFIX>-tf-state` (for storing the terraform state file)
- `<PREFIX>-orca-archive-worm`
- `<PREFIX>-orca-reports`

Note that the `<PREFIX>-orca-primary`, `<PREFIX>-orca-archive-worm` and `<PREFIX>-orca-reports` buckets should be created in the DR OU if we want a full test. This will also need a cross account policy applied to it as well which should be similar to this [policy](https://github.com/nasa/cumulus-orca/blob/develop/website/docs/developer/research/research-s3-bucket-policies.md#reports-bucket).

The bucket can be created using the following CLI command:
```bash
aws s3api create-bucket --bucket <BUCKET_NAME>  --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
```
In addition to this, the dynamodb table and bucket version need to created as well.
```bash
   aws dynamodb create-table \
      --table-name <PREFIX>-tf-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region us-west-2
```

```bash
      aws s3api put-bucket-versioning \
    --bucket <PREFIX>-tf-state \
    --versioning-configuration Status=Enabled
```

The EC2 key pair can be created using the AWS CLI:

```bash
aws ec2 create-key-pair --key-name <PREFIX>
```

For `Deploy buckets in DR account` stage in bamboo plan, add the values for `PREFIX`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` variables for the `Disaster Recovery` AWS account to deploy the buckets in DR account.

For the `Deploy Dev Cumulus and ORCA Stack`  stage, add the following variables. 

- RDS_SECURITY_GROUP
- RDS_USER_ACCESS_SECRET_ARN
- DB_HOST_ENDPOINT
- EARTHDATA_CLIENT_ID
- EARTHDATA_CLIENT_PASSWORD
- CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION

The RDS variables `RDS_SECURITY_GROUP`, `RDS_USER_ACCESS_SECRET_ARN` and `DB_HOST_ENDPOINT` can be found from output logs of the previous `Deploy Dev RDS Stack` stage. Note that a new earthdata application will need to be first created if using a new prefix for new deployment which will give the values for `EARTHDATA_CLIENT_ID` and `EARTHDATA_CLIENT_PASSWORD`. `CUMULUS_ORCA_DEPLOY_TEMPLATE_VERSION` is the branch you want to check out in the [deployment repo](https://git.earthdata.nasa.gov/projects/ORCA/repos/cumulus-orca-deploy-template/browse) such as `v11.1.1-v4.0.1`.

Note that `RDS_USER_ACCESS_SECRET_ARN` value from the initial run should be recorded, as they may be hidden on future deployments. In addition, the jobs may need to be run multiple times to get past deployment errors if there is one. If an error is raised saying `Cloudwatch log groups already exist`, then manually delete all the cloudwatch log groups and corresponding lambdas having the same name as the log groups from the AWS console and retry running the job.