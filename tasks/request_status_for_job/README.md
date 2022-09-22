[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_status_for_job/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_status_for_job/requirements.txt)

**Lambda function request_status_for_job **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_job](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```

### Example Output
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "jobStatusTotals": {
    "pending": 1,
    "success": 1,
    "failed": 1
  },
  "granules": [
    {
      "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
      "status": "failed"
    },
    {
      "granuleId": "b5681dc1-48ba-4dc3-877d-1b5ad97e8276",
      "status": "pending"
    },
    {
      "granuleId": "7a75767d-abe3-4c1d-b55f-9009de1838f8",
      "status": "success"
    }
  ]
}
```
<a name="pydoc"></a>
## pydoc request_status_for_job
[See the API documentation for more details.](API.md)