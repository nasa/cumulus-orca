[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/internal_reconcile_report_job/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/internal_reconcile_report_job/requirements.txt)

**Lambda function internal_reconcile_report_job **

Receives page index from end user and returns available internal reconciliation jobs from the Orca database.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc internal_reconcile_report_job](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see bin/build.sh to build the zip file. Upload the zip file to AWS.
    
```
<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "pageIndex": 0
}
```
### Example Output
```json
{
  "anotherPage": false,
  "jobs": [
    todo
  ]
}
```
<a name="pydoc"></a>
## pydoc internal_reconcile_report_job
[See the API documentation for more details.](API.md)