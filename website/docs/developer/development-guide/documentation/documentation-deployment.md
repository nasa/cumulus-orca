---
id: contrib-documentation-deploy
title: Deploying Documentation
desc: Provides basic information on deploying ORCA documentation to nasa.github.io
---

The following sections provide information to ORCA users to create automated or
manual releases on github. View the entire versioning and releases document 
[here](https://github.com/nasa/cumulus-orca/blob/master/docs/release.md).

Additional deployment information can be found at the [Docusaurus deployment page](https://docusaurus.io/docs/deployment).

## Automated Documentation Release on Github

### Create a new ORCA release on github

The release is automated in Bamboo, but the step must be manually started. If 
you set the `RELEASE_FLAG` to `true` and the build steps passed, you will be 
able to run the manual "Release" step in Bamboo.

On a successful automated release, the updated documentation is committed to the
`gh-pages` branch of the [Cumulus ORCA repo](https://github.com/nasa/cumulus-orca).
The updated documentation should be available on the Cumulus ORCA website at
https://nasa.github.io/cumulus-orca.

### Merge the base branch into develop and master

Merge the version update changes back into develop and master.

If this is the latest version, you can simply create a PR to merge the release 
branch into develop and master. Note: Do not squash this merge. Doing so will 
make the "compare" view from step 4 show an incorrect diff, because the tag is 
linked to a specific commit on the base branch.

## Manual Documentation Release on Github

Use the following steps to update Github documentation manually.

:::important Important

* Users need **Node 1215** installed to perform manaul updates to documentation.
* The `Deployment_Branch` must = **gh-pages**.
:::

1. Clone the Cumulus ORCA repo to your machine. Enter the repo directory and change to 
   the proper branch.

```
git clone https://github.com/nasa/cumulus-orca.git
cd cumulus-orca
git checkout release-X.Y.Z
```

 2. Enter the `website` directory

```
cd website
```

 3. Export the needed environment variables. Make sure to use your GitHub username and 
    password.

```
export DEPLOYMENT_BRANCH=gh-pages
export GIT_USER=$bamboo_SECRET_GITHUB_USER
export GIT_PASS=$bamboo_SECRET_GITHUB_TOKEN
```

 4. If your user email and username configuration is not set for git, that must be 
    done before running the deploy in order to avoid errors when pushing to the GitHub 
    repository. If the config is set, this step can be skipped.

```
git config --global user.email "$bamboo_SECRET_GITHUB_EMAIL"
git config --global user.name "$GIT_USER"
```

 5. Run the deployment script via npm.

```
npm run deploy
```


