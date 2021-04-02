---
id: contrib-documentation-deploy
title: Deploying Documentation
desc: Provides basic information on deploying ORCA documentation to nasa.github.io
---

The following sections provide information to ORCA users to create automated or
manual releases on github. View the entire versioning and releases document 
[here](https://github.com/nasa/cumulus-orca/blob/master/docs/release.md).

## Automated Documentation Release on Github

### Create a new ORCA release on github

The release is automated in Bamboo, but the step must be manually started. If 
you set the `RELEASE_FLAG` to `true` and the build steps passed, you will be 
able to run the manual "Release" step in Bamboo.

The CI release scripts will create a release based on the release version tag, 
as well as uploading release artifacts to the Github release for the Terraform 
modules provided by Cumulus. The Terraform release artifacts include:

 * A multi-module Terraform .zip artifact containing filtered copies of the 
   tf-modules, packages, and tasks directories for use as Terraform module sources.

Just make sure to verify the appropriate .zip files are present on Github after 
the release process is complete.

### Merge the base branch into develop and master

Merge the version update changes back into develop and master.

If this is the latest version, you can simply create a PR to merge the release 
branch into develop and master. Note: Do not squash this merge. Doing so will 
make the "compare" view from step 4 show an incorrect diff, because the tag is 
linked to a specific commit on the base branch.

## Manual Documentation Release on Github

Use the following steps to update Github documentation manually.

::: Important

* Users need **Node 1215** installed to perform manaul updates to documentation.
* The `Deployment_Branch` must = **gh-pages**.
:::

```
## MAIN
## -----------------------------------------------------------------------------
## Release the Documentation
# Go to the documentation directory
check_rc "cd website"

# Install Node.js and the proper packages
check_rc "npm install"

## Run the deployment See: https://docusaurus.io/docs/deployment
# Set the environment variables
export DEPLOYMENT_BRANCH=gh-pages
export GIT_USER=$bamboo_SECRET_GITHUB_USER
export GIT_PASS=$bamboo_SECRET_GITHUB_TOKEN

# We need to set some git config here so deploy doesn't complain when the 
commit occurs.
git config --global user.email "$bamboo_SECRET_GITHUB_EMAIL"
git config --global user.name "$GIT_USER"

check_rc "npm run deploy"

cd ..

exit 0
```


