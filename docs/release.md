# Versioning and Releases

Much of this documentation is borrowed straight from [Cumulus](https://github.com/nasa/cumulus/blob/master/docs/development/release.md).

## Versioning

We use semantic versioning. Read more about semantic versioning [here](https://semver.org/).

## Release Process

### 1. Create a release branch

From develop, create a new release branch following the `release/MAJOR.MINOR.x` pattern. For example, `release/1.0.0`. Push this branch to github if you created it locally.

### 2. Update CHANGELOG.md

Update the CHANGELOG.md. Put a header under the 'Unreleased' section with the new version number and the date.

### 3. Create a pull request against the new version branch

Create a PR, verify that Bamboo builds succeed, and then merge into the version branch.

### 4. Create a git tag for the release

Check out the minor version base branch now that your changes are merged and do a git pull. Ensure you are on the latest commit.

Create and push a new git tag:
```
  git tag -a v1.x.x -m "Release 1.x.x"
  git push origin v1.x.x
```

### 5. Running the deployment

Publishing of new releases is handled by a Bamboo release plan and is manually triggered.

If you created a new release plan in step one, you will need to create a new bamboo deployment plan

#### Creating a Bamboo Deployment Plan

* In the ORCA project (https://ci.earthdata.nasa.gov/browse/ORCA-OI), click `Actions -> Configure Plan` at the top right.
* Scroll to the bottom of the branch list in the bottom left and select `Create Plan Branch`.
* Add the values in that list. Choose a display name that makes it very clear this is a deployment branch plan. Release (branch name) seems to work well. Make sure you enter the correct branch name.
* Important Deselect Enable Branch - if you do not do this, it will immediately fire off a build.
* Do Immediately On the Branch Details page, enable Change trigger. Set the Trigger type to manual, this will prevent commits to the branch from triggering the build plan. You should have been redirected to the Branch Details tab after creating the plan. If not, navigate to the branch from the list where you clicked Create Plan Branch in the previous step.
* Go to the Variables tab. Ensure that you are on your branch plan and not the master plan: You should not see a large list of configured variables, but instead a dropdown allowing you to select variables to override, and the tab title will be Branch Variables. Set a DEPLOYMENT variable appropriate for the release (defaults to last committer). This should be cumulus-from-npm-tf except in special cases such as incompatible backport branches. Then set:
  * ORCA_VERSION: `<version number>`
  * RELEASE_FLAG: true
* Enable the branch from the Branch Details page.
* Run the branch using the Run button in the top right.

Bamboo will build and run unit tests against that tagged release.

#### Create a new ORCA release on github

The CI release scripts will automatically create a release based on the release version tag, as well as uploading release artifacts to the Github release for the Terraform modules provided by Cumulus. The Terraform release artifacts include:
* A multi-module Terraform .zip artifact containing filtered copies of the tf-modules, packages, and tasks directories for use as Terraform module sources.

Just make sure to verify the appropriate .zip files are present on Github after the release process is complete.

#### Merge the base branch back into master

Finally, you need to reproduce the version update changes back to master.

If this is the latest version, you can simply create a PR to merge the minor version base branch back to master. Note: Do not squash this merge. Doing so will make the "compare" view from step 4 show an incorrect diff, because the tag is linked to a specific commit on the base branch.

### Troubleshooting

#### Delete and regenerate the tag

To delete a published tag to re-tag, follow these steps:
```
  git tag -d v1.x.x
  git push -d origin v1.x.x
```
