---
id: deployment-upgrading-orca
title: Upgrading ORCA
description: Provides developer with information on upgrading ORCA.
---

After the initial ORCA deployment, any future updates to the ORCA deployment
from configuration files, Terraform files (`*.tf`), or modules from a new
version of ORCA can be deployed and will update the appropriate portions of
the stack as needed.

:::important Ensure Cumulus Compatibility
Check for compatibility with the [Cumulus version](https://wiki.earthdata.nasa.gov/display/CUMULUS/Supported+PI+Versions).
:::

## ORCA Versioning

ORCA uses a global versioning approach, meaning version numbers are
consistent across all Terraform modules and semantic versioning to track
major, minor, and patch version (e.g., 1.0.0).

:::important
ORCA major version releases (e.g., 2.x.x -> 3.x.x) introduce known breaking
changes. However, any version change has the possibility to introduce breaking
changes for your particular use case. It is critical that the release notes
are viewed for migration steps and changes.
:::

Carefully read each 'Migration Notes'
section within the `CHANGELOG.md` file, following all steps, starting with the oldest release after your
currently installed release, and progressing through them chronologically.

To view the released module artifacts for each ORCA core
version, see the [ORCA Releases page](https://github.com/nasa/cumulus-orca/releases).

## Migrating to a New Version

When breaking changes have been introduced, the ORCA Team will publish
instructions on migrating from one version to another. Detailed release notes
with migration instructions (if any) for each release can be found on the
[ORCA Releases page](https://github.com/nasa/cumulus-orca/releases).

1.	**Use consistent ORCA versions:** All Terraform modules must be updated
to the same ORCA version number (see Updating ORCA Version below). **Check
the CHANGELOG for deprecation/breaking change notices.**

2.	**Follow all intervening steps:** When skipping over versions, **you must
perform all intervening migration steps.** For example, if going from version
1.1.0 to 1.3.0, upgrade from 1.1.0 to 1.2.0 and then to 1.3.0. This is
critical because each release that contains migration steps provide
instructions *only* for migrating from the *immediately* previous release,
but you must follow *all* migration steps between your currently installed
release and *every release* through the release that you wish to migrate to.

3.	**Migrate lower environments first:** Migrate your "lowest" environment
first and test it to ensure correctness before performing migration steps in
each successively higher environment. For example, update Sandbox, then UAT,
then SIT, and finally Prod.

4.	**Conduct smoke tests:** In each environment, perform smoke tests that
give you confidence that the upgrade was successful, prior to moving on to
the next environment. Since deployments can vary widely, it is up to you to
determine tests that might be specific to your deployment.

5.	**Migrate during appropriate times:** Choose a time to migrate when
support is more likely to be available in case you encounter problems, such
as when you are most likely to be able to obtain support relatively promptly.
Prefer earlier in the week over later in the week (particularly avoiding
Fridays, if possible).

## Updating ORCA Version

To update your ORCA version:

1.	Find the desired release on the [ORCA Releases page](https://github.com/nasa/cumulus-orca/releases).

2.	Update the `source` in your Terraform deployment files for ORCA by
replacing `vx.x.x` with the desired version of ORCA. If upgrading from `v8.x.x` to `v9.x.x` follow the below steps:
    1. Run the Lambda deletion script found in `python3 bin/delete_lambda.py` this will delete all of the ORCA Lambdas with a provided prefix. Or delete them manually in the AWS console.
    2. Navigate to the AWS console and search for the Cumulus RDS security group.
    3. Remove the inbound rule with the source of `PREFIX-vpc-ingress-all-egress` in Cumulus RDS security group.
    4. Search for `PREFIX-vpc-ingress-all-egress` and delete the security group **NOTE:** Due to the Lambdas using ENIs, when deleting the securty groups it may say they are still associated with a Lambda that was deleted by the script. AWS may need a few minutes to refresh to fully disassociate the ENIs completely, if this error appears wait a few minutes and then try again.

3.	Run `terraform init` to get the latest copies of your updated modules.

## Update ORCA Resources

:::note Reminder
Remember to [initialize Terraform](https://nasa.github.io/cumulus/docs/deployment/deployment-readme#initialize-terraform)
if necessary.
:::

From the directory of your `cumulus` deployment module (e.g., `cumulus-tf`):

`$ AWS_REGION=<region> \ # e.g. us-west-2`
    `AWS_PROFILE=<profile> \`
    `terraform apply`

Once you have successfully updated all of your resources, verify that your
deployment functions correctly. Please refer to some recommended smoke tests
given above and consider additional tests appropriate for your particular
deployment and environment.

