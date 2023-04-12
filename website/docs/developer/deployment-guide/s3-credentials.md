---
id: deployment-s3-credentials
title: Generating S3 credentials
description: Provides developer with information on archive storage solutions.
---

Postgres requires access to the [ORCA Reports bucket](./creating-orca-archive-bucket.md#reports-bucket) to pull in s3 inventory information.
These values are stored in the [Required Variables](./deployment-with-cumulus.md#orca-required-variables) `s3_access_key` and `s3_secret_key`.
Note that this only impacts [Internal Reconciliation reports](../api/api.md#internal-reconcile-report-jobs-api), which is not required for ingest or recovery, but is helpful for verifying data integrity.
If you are unable to follow these instructions, or wish to avoid generating/managing credentials, blank values may be used and the impact will be isolated to Internal Reconciliation.

To generate an access key:
1. Connect to the NASA VPN.
1. Go to https://cloud.earthdata.nasa.gov/portal/project
1. Click the account containing your ORCA Reports bucket
1. `CLOUD MANAGEMENT` -> `AWS Long-Term Access Keys`
1. Under the revealed `AWS Long-Term Access Keys` sections, click the three dots, followed by `Create AWS long-term access keys`
1. Select an account and role that can access the bucket
1. Click `Generate API Key`
1. Make sure to copy the secret value from this screen. This is your `s3_secret_key`. The `Key ID` is your `s3_access_key`
1. Note that these keys will eventually expire and will need to be regenerated and redeployed

We are looking into alternatives to this system to remove these manual steps and eliminate the need for manual redeployment of expired keys.
