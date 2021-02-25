[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_files_to_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function request_status_for_granule **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc request_status_for_granule](#pydoc-copy-files)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input with granule_id and asyncOperationId.
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```
Input with no asyncOperationId. Only the most recent operation for the granule will be queried.
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250"
}
```

### Example Output
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "file_name": "f1.doc",
      "status": "pending"
    },
    {
      "file_name": "f2.pdf",
      "status": "failed",
      "error_message": "Access Denied"
    },
    {
      "file_name": "f3.txt",
      "status": "success"
    }
  ],
  "restore_destination": "bucket_name",
  "request_time": "2019-07-17T17:36:38.494918",
  "completion_time": "2019-07-18T17:36:38.494918"
}
```

