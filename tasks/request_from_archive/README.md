[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_from_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_from_archive/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

**Lambda function request_from_archive**

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [Input/Output Schemas](#input-output-schemas)
- [pydoc request_from_archive](#pydoc)

## Deployment
```
    see bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  The easiest way to test is to use the DrRecoveryWorkflowStateMachine.
    You can use the test event in tasks/extract_filepaths_for_granule/test/testevents/StepFunction.json.
    Edit the ['payload']['granules']['keys'] values as needed to be the file(s) you wish to restore.
    Edit the ['cumulus_meta']['execution_name'] to be something unique (like yyyymmdd_hhmm). Then
    copy and paste the same value to the execution name field above the input field.
    The restore may take up to 5 hours.
Use the AWS CLI to check status of restore request:
ex> (podr) λ aws s3api head-object --bucket podaac-sndbx-cumulus-archive --key L0A_RAD_RAW_product_0001-of-0020.iso.xml
```

## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "granules": 
  [
    {
      "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
      "keys": [
        {
          "key": "survey/local/L0A_LR_RAW_product_0010-of-0092.h5",
          "destBucket": "some_bucket_name"
        }
      ]
    }
  ]
}
```

### Example Output
```json
{
  "granules":
  [
    {
      "granuleId": "MOD09GQ.A0219114.N5aUCG.006.0656338553321",
      "recoverFiles":
      [
        {
          "filename": "L0A_LR_RAW_product_0010-of-0092.h5",
          "keyPath": "survey/local/L0A_LR_RAW_product_0010-of-0092.h5",
          "last_update": "2022-05-31T18:54:11.477875+00:00",
          "restoreDestination": "some_bucket_name",
          "requestTime": "2022-05-31T18:54:11.477875+00:00",
          "statusId": 1,
          "success": true,
          "s3MultipartChunksizeMb": null
        }
      ]
    }
  ],
  "asyncOperationId": "yourJobId"
}
```

<a name="pydoc"></a>
## pydoc request_from_archive
[See the API documentation for more details.](API.md)