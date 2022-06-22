[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/get_current_archive_list/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/get_current_archive_list/requirements.txt)

**Lambda function get_current_archive_list **

Receives a list of s3 events from an SQS queue, and loads the s3 inventory specified into postgres.
Events must be for manifest.json files that correspond to s3 inventory reports.
Data is used in Reconciliation processes to compare against the Orca internal catalog.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas](#input-output-schemas)
- [pydoc get_current_archive_list](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "reportBucketRegion": "us-west-2",
  "reportBucketName": "PREFIX-orca-reports",
  "manifestKey": "PREFIX-orca-primary/reportname/2022-01-14T00-00Z/manifest.json"
}
```

### Example Output
```json
{
    "jobId": 3,
    "orcaArchiveLocation": "PREFIX-orca-primary",
    "messageReceiptHandle": "MbZj6wDWli+JvwwJaBV+3dcjk2YW2vA3+STFFljTM8tJJg6HRG6PYSasuWXPJB+CwLj1FjgXUv1uSj1gUPAWV66FU/WeR4mq2OKpEGYWbnLmpRCJVAyeMjeU5ZBdtcQ+QEauMZc8ZRv37sIW2iJKq3M9MFx1YvV11A2x/KSbkJ0="
}
```

<a name="pydoc"></a>
## pydoc get_current_archive_list
[See the API documentation for more details.](API.md)