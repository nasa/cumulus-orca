[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function request_status_for_granule **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_granule](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input with granule_id and asyncOperationId.
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```
Input with no asyncOperationId. Only the most recent operation for the granule will be queried.
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250"
}
```

### Example Output
```json
{
  "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "fileName": "f1.doc",
      "status": "pending"
    },
    {
      "fileName": "f2.pdf",
      "status": "failed",
      "errorMessage": "Access Denied"
    },
    {
      "fileName": "f3.txt",
      "status": "success"
    }
  ],
  "restoreDestination": "bucket_name",
  "requestTime": 628021800000,
  "completionTime": 628021900000
}
```
<a name="pydoc"></a>
## pydoc request_status_for_granule
[See the API documentation for more details.](API.md)