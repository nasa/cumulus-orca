[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/shared_libraries/requirements-test.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/requirements-test.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for additional information on environment setup and [running/creating tests](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/integration-tests).

## Ingest Integration Test in Bamboo
The `ORCA Deploy Plan` under ORCA project in Bamboo includes the ingest integration test which will run automatically once ORCA deployment is successful. See [ORCA deployment doc](https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/development-guide/code/versioning-releases.md#deploying-orca-buckets-rds-cluster-and-cumulus-orca-modules-via-bamboo) for more information.

## Test cleanup

1. Connect to NASA VPN. In two separate terminals, run the following commands. Remember to replace the variables inside <>.

```
ssh -p 6868 -L 5432:<PREFIX>-<RDS_ENDPOINT>:5432 -i "<EC2_KEY_PAIR.pem>" -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1
```
```
aws ssm start-session --target <EC2_INSTANCE_ID> --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868
```
2. Export `orca_RECOVERY_BUCKET_NAME`, `SOURCE_BUCKET_NAME` and `DB_CONNECT_INFO_SECRET_ARN` variables locally.

3. Make sure the SSM and SSH connections are still active. Then run `python cleanup/test-cleanup.py` from integration_test directory.

:::note
Since the cleanup script requires connection to AWS SSM as well as to the database, running the cleanup script in Bamboo is not compatible at the moment.
:::