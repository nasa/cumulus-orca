---
id: deploying-from-mac
title: Deploy Cumulus dashboard from Mac
description: A concrete set of instructions on deploying Cumulus dashboard from Mac to create a test environment for ORCA. Also includes instructions for deploying the dashboard with launchpad authentication.
---

import useBaseUrl from '@docusaurus/useBaseUrl';

The goal of this page is to provide a set of additional instructions that will be useful to deploy the dashboard locally from Mac for ORCA project. It is assumed that Cumulus and ORCA are already deployed before following these instructions. Follow instructions on the following link on how to deploy Cumulus and ORCA:

 - https://nasa.github.io/cumulus/docs/deployment/deployment-readme
 - https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus

## Setting up tunneling to locally run the dashboard

There are several steps involved to set up tunneling to use the dashboard locally.

- Create a pac file named `aws-proxy.pac` under your `user/.ssh` directory and add the following function to that file:

```bash
function FindProxyForURL (url, host) {
 // Redirect for Cumulus-ORCA Dashboard
if (dnsDomainIs(host, '<YOUR_API_ENDPOINT_URL>')) {
 return 'SOCKS5 localhost:1337';
}
// by default use no proxy
return 'DIRECT';
}
```

  Replace `<YOUR_API_ENDPOINT_URL>` with your Cumulus API endpoint found from terraform output named as `archive_api_uri` under module `cumulus-tf`.

1. Firefox browser is used to view the dashboard. On Firefox browser, go to `Setting`-> `Network Settings`. Under `Automatic proxy configuration URL`, add the path to your `aws-proxy.pac` file in this format `file:///Users/<username>/.ssh/aws-proxy.pac`. Replace `<username>` with yours.
2. Connect to NASA VPN, then run the following command from your bash terminal:
  ```bash
  aws ssm start-session --target i-0edf895d1b2f8447d --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868
  ```

  Replace instance-id `i-0edf895d1b2f8447d` with your Cumulus deployed EC2 instance ID. You can get this from EC2 dashboard in AWS and should be named `<prefix>-Cumulus-ECSCluster`.
3. On another bash terminal, run 
    ```bash
    ssh -vvv -p 6868 -N -D 1337 -i ~/.ssh/<YOUR_AWS_PRIVATE_KEY.pem> -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1
    ```

  Replace `<YOUR_AWS_PRIVATE_KEY.pem>` with yours. The pem file should have been created while deploying the `cumulus-tf` module via terraform. If not, go to your EC2 dashboard from AWS console and click `Key Pair` field. Then create a new EC2 key pair with your prefix name and download the `.pem` file to your `user/.ssh` directory.

 :::important
  The key pair name must match the prefix name used in `cumulus-tf/terraform.tfvars` file orelse it will not connect to the instance.
 :::

 :::note
 Port -p 6868 should match the localPortNumber=6868 port number in your AWS SSM session.
 :::

 4. The next step is to deploy the dashboard. Clone the repository using 
 
    ```bash
   git clone https://github.com/nasa/cumulus-dashboard.git
   ```

 Then under your `cumulus-dashboard` directory, run 
  
   ```bash
   npm install
   ```

   Once that is done, run the following command by replacing `<YOUR_API_ENDPOINT>` with your Cumulus API endpoint found from terraform output.

    ```bash
   ENABLE_RECOVERY=true APIROOT=<YOUR_API_ENDPOINT> npm run serve
   ```

 5. Once the website is running, go to Firefox and put in `http://localhost:3000/` to access the dashboard.   
 
   :::important
   Make sure the SSM and SSH sessions are both running.
   :::important


## Deploying the dashboard with launchpad authentication

A workflow request followed by a NAMS request has to be created and approved first before the launchpad authentication can be used. Check https://idmax.nasa.gov/nams/asset/255115

:::note
There might be some issues while creating the workflow request. Contact ORCA team while creating the NAMS request.

:::

Once the workflow and NAMS request are approved, proceed to the following steps.

1. Go to your AWS S3 console and search for `<prefix>-internal` bucket. Under `<prefix>-internal/<prefix>/` directory, create a new folder `crypto`.
   Upload the two files `launchpadMetadata.xml` and `launchpad.pfx` under `<prefix>-internal/<prefix>/crypto`. 
   Contact ORCA team if you do not have access to those files.
2. Update your `cumulus-tf/terraform.tfvars` file to include the following variables:
    
   ```
    cmr_oauth_provider = "launchpad"
    oauth_provider   = "launchpad"
    launchpad_api = "https://api.launchpad.nasa.gov/icam/api/sm/v1"
    # using the standard path, which is <prefix>/crypto/launchpad.pfx in the system bucket
    # launchpad_certificate = "certificate"
    launchpad_passphrase = "35kbMfH25Y4JjCBfoj7XBig!"
    oauth_user_group = "LPDAAC-cumulus-operator-uat"
    # see Wiki: https://wiki.earthdata.nasa.gov/display/CUMULUS/Cumulus+SAML+Launchpad+Integration
    saml_entity_id                  = "https://<YOUR_API_ENDPOINT>"
    saml_assertion_consumer_service = "https://<YOUR_API_ENDPOINT>/saml/auth"
    saml_idp_login                  = "https://auth.launchpad.nasa.gov/affwebservices/public/saml2sso"
    saml_launchpad_metadata_url     = "https://auth.launchpad.nasa.gov/unauth/metadata/launchpad.idp.xml"

   ```

   Replace `<YOUR_API_ENDPOINT>` with your Cumulus API endpoint found from terraform output.

3. Rerun `terraform apply` to deploy the updates under `cumulus-tf`.


4. Follow all the steps under `Setting up tunneling to locally run the dashboard` until the `npm install` command in step 4. Then 
   run the following command with the additional field `AUTH_METHOD=launchpad`:

   `AUTH_METHOD=launchpad ENABLE_RECOVERY=true APIROOT=<YOUR_API_ENDPOINT> npm run serve`

   Replace `<YOUR_API_ENDPOINT_URL>` with yours. Then complete the rest of the steps in `Setting up tunneling to locally run the dashboard` normally.
5. Once the website is running, go to Firefox and put in `http://localhost:3000/` to access the dashboard.   
 
   :::warning
   The dashboard will show a 403 error if there is any issue with the NAMS request for launchpad.
   :::