[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/internal_reconcile_report_phantom/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/internal_reconcile_report_phantom/requirements.txt)

**Lambda function internal_reconcile_report_phantom **

Receives job id and page index from end user and returns reporting information of files that have records in the ORCA catalog but are missing from S3 bucket.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc internal_reconcile_report_phantom](#pydoc)

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
  "jobId": 123,
  "pageIndex": 0
}
```
### Example Output
```json
{
  "jobId": 123,
  "anotherPage": false,
  "phantoms": [
    {
      "collectionId": "MOD09GQ___061",
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "filename": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "orcaEtag": "d41d8cd98f00b204e9800998ecf8427",
      "orcaLastUpdate": 628021970000,
      "orcaSize": 6543277389
    }
  ]
}
```
<a name="pydoc"></a>
## pydoc internal_reconcile_report_phantom
[See the API documentation for more details.](API.md)