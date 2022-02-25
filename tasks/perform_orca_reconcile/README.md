[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/perform_orca_reconcile/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/perform_orca_reconcile/requirements.txt)

**Lambda function perform_orca_reconcile **

Compares entries in reconcile_s3_objects to the Orca catalog,
writing differences to reconcile_catalog_mismatch_report, reconcile_orphan_report, and reconcile_phantom_report.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc perform_orca_reconcile](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "jobId": 123,
  "orcaArchiveLocation": "prefix-orca-primary",
}
```
### Example Output
```json
{
  "jobId": 123
}
```

<a name="pydoc"></a>
## pydoc perform_orca_reconcile
See API.md for documentation.