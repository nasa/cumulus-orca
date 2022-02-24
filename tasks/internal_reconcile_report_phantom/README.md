[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/internal_reconcile_report_phantom/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/internal_reconcile_report_phantom/requirements.txt)

**Lambda function internal_reconcile_report_phantom **

Receives job id and page number from end user and returns reporting information of files that have records in the ORCA catalog but are missing from S3 bucket.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc internal_reconcile_report_phantom](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc internal_reconcile_report_phantom
[See the API documentation for more details.](API.md)