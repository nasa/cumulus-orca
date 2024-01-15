# Overview

The Operational Recovery Cloud Archive (ORCA) provides a baseline solution for creating, storing, and managing operational backups in the cloud. In addition, best practices and recovery code that manages common baseline recovery scenarios is also maintained. Requirements and use cases for ORCA are derived from the ORCA Working Group.

## ORCA Static Documentation

ORCA documentation can be found at [nasa.github.io/cumulus-orca](https://nasa.github.io/cumulus-orca).
The documentation is available for developers, data managers, and users.
Additional documentation is being added continually.

Make sure you are using the latest LTS node.js versions to view the documentation.

- npm 9.x
- node 20.x

Further ORCA documentation can be read locally by performing the following:

```sh
cd website
npm install
npm run start
```

Once the server is running, documentation should be available on `http://localhost:3000`.

## ORCA Deployment

The ORCA deployment is done with [Terraform](https://www.terraform.io/).

Currently, Orca should only be deployed as an integration with Cumulus.
See [deployment documentation](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus/)
for steps and other documentation.
