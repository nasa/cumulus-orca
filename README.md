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

Currently, Orca should only be deployed as an integration with Cumulus.
See [deployment documentation](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus/)
for steps and other documentation.

## Release Documentation:

Information about how to create an ORCA release can be found [here](docs/release.md).
