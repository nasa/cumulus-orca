---
id: contrib-documentation-env
title: Development Environment
desc: Provides basic information on setting up an ORCA documentation development environment.
---
Editing and updating the website only requires a text editor and git but, in
order to verify links and the overall website build, a local development environment
should be created. This pages discusses the setup, running, building, and testing
of the Docusarus website for the ORCA GitHub pages.

## Creating the Development Environment

Setting up the development environment consists of three primary tasks,
- Cloning the cumulus-orca GitHub repository
- Installing the proper Node.js and npm versions
- Installing the proper node packages for the cumulus-orca documentation.

The installation steps below goes into further details.

1. Install the latest [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm) application to manage Node.js and npm versions.
   ```sh
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
   ```

2. Install the proper Node.js and npm versions to your machine. Currently Node v12.15.0 should be used.
   ```sh
   nvm install 12.15.0
   nvm use 12.15.0
   npm install npm@latest -g
   ```

3. Clone the cumulus-orca repository to your local machine.
   ```sh
   git clone https://github.com/nasa/cumulus-orca.git
   ```

4. Move to the `website` directory under the cumulus-orca local git repository.
   ```sh
   cd cumulus-orca/website
   ```

5. Install the additional node packages needed to create and validate the webpages.
   ```sh
   npm install
   ```


## Installing the Test Harness

TBD - Automated testing that includes link checking is currently being looked into.


## Running the Development Server

To run the development web server and verify builds, contents, and styles perform
the following commands. More information on running a Docusaurus website can be
found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/installation#running-the-development-server).

```sh
## From the repository base move to the website directory.
cd website

## Start the server on port 8080 with verbose output for debugging
npm run start --verbose -- --port 8080
```

A new webpage should display in your default browser at [http://localhost:8080](http://localhost:8080).


## Building the ORCA Website Locally

To build the cumulus-orca static website for GitHub pages locally run the
commands seen below. More information on building a Docusaurus website can be
found in the [Docusaurus documentation](https://v2.docusaurus.io/docs/installation#build).

```sh
## From the repository base move to the website directory.
cd website

## Build the site
npm run build
```

The resulting site can be found in the `build` directory.


