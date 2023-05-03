[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/shared_libraries/requirements-test.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/requirements-test.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for additional information on environment setup and [running/creating tests](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/integration-tests).

## Test cleanup

In order to cleanup data from the buckets and catalog, run `python cleanup/test-cleanup.py` from integration_test directory. Remember to export `orca_RECOVERY_BUCKET_NAME`, `SOURCE_BUCKET_NAME` and `DB_CONNECT_INFO_SECRET_ARN` variables locally first.