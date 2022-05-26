[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/request_files/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/request_files/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

**Lambda function request_files**

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc request_files](#pydoc-request-files)

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
ex> (podr) λ aws s3api head-object --bucket podaac-sndbx-cumulus-glacier --key L0A_RAD_RAW_product_0001-of-0020.iso.xml
```
<a name="pydoc-request-files"></a>
## pydoc request_files
[See the API documentation for more details.](API.md)