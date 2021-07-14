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

1. In the ORCA project (https://ci.earthdata.nasa.gov/browse/ORCA-OI), click
   `Actions -> Configure Plan` at the top right.
2. Scroll to the bottom of the branch list in the bottom left and select
   `Create Plan Branch`.
3. Add the values in that list. Choose a display name that makes it very clear 
   this is a deployment branch plan. Release (branch name) seems to work well. 
   Make sure you enter the correct branch name.
4. Important Deselect Enable Branch - if you do not do this, it will immediately
   fire off a build.
5. Do Immediately On the Branch Details page, enable 'Change Trigger'. Set the 
   Trigger type to manual, and this will prevent commits to the branch from 
   triggering the build plan. You should have been redirected to the 'Branch 
   Details' tab after creating the plan. If not, navigate to the branch from
   the list where you clicked 'Create Plan Branch' in the previous step.
6. Go to the Variables tab. Ensure that you are on your branch plan and not the
   master plan: You should not see a large list of configured variables, but 
   instead a dropdown allowing you to select variables to override, and the tab 
   title will be Branch Variables. Set a DEPLOYMENT variable appropriate for the
   release (defaults to last committer). This should be cumulus-from-npm-tf 
   except in special cases such as incompatible backport branches. Then set:
     * ORCA_VERSION: `<version number>`
     * RELEASE_FLAG: true
7. Enable the branch from the 'Branch Details' page.
8. Run the branch using the 'Run' button in the top right.

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

