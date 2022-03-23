[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/get_current_archive_list/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/get_current_archive_list/requirements.txt)

**Lambda function get_current_archive_list **

Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.
Events must be for manifest.json files that correspond to s3 inventory reports.
Data is used in Reconciliation processes to compare against the Orca internal catalog.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc get_current_archive_list](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc get_current_archive_list
[See the API documentation for more details.](API.md)