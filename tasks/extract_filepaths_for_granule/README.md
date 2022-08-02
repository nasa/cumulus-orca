[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/extract_filepaths_for_granule/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/extract_filepaths_for_granule/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

## Description

The module `extract_filepaths_for_granule` is deployed as a lambda function that extracts the keys (filepaths) for a granule's files from a Cumulus Message.

## Build

The following steps assume you are using a version of Python compliant with 3.7.

```
cd tasks\extract_filepaths_for_granule
rm -rf build
rm -rf venv
mkdir build
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -q -t build -r requirements.txt --trusted-host pypi.org --trusted-host pypi.org --trusted-host files.pythonhosted.org
deactivate
cp *.py build/
cd build
zip -r ../extract_filepaths_for_granule.zip .
cd ..
```
An example of a script for building the `extract_filepaths_for_granule` lambda package can be found in `/tasks/extract_filepaths_for_granule/bin/build_tasks.sh`.

## Unit tests

Unit tests for `extract_filepaths_for_granule` lambda function can be run using 

```
coverage run --source extract_filepaths_for_granule -m pytest
```
See the script under `tasks/extract_filepaths_for_granule/bin/run_tests.sh`

## Deployment

Use the `extract_filepaths_for_granule.zip` file from build step to deploy the lambda by passing this to `filename` argument in terraform section.
The `modules/lambdas/main.tf` shows an example of deploying this lambda through Terraform.

```
# extract_filepaths_for_granule - Translates input for request_files lambda
# ==============================================================================
resource "aws_lambda_function" "extract_filepaths_for_granule" {
  ## REQUIRED
  function_name = "${var.prefix}_extract_filepaths_for_granule"
  role          = module.restore_object_arn.restore_object_role_arn

  ## OPTIONAL
  description      = "Extracts bucket info and granules filepath from the CMA for ORCA request_files lambda."
  filename         = "${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip"
  handler          = "extract_filepaths_for_granule.handler"
  memory_size      = var.orca_recovery_lambda_memory_size
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../tasks/extract_filepaths_for_granule/extract_filepaths_for_granule.zip")
  tags             = local.tags
  timeout          = var.orca_recovery_lambda_timeout

  vpc_config {
    subnet_ids         = var.lambda_subnet_ids
    security_group_ids = [module.lambda_security_group.vpc_postgres_ingress_all_egress_id]
  }
}
```
### Deployment Validation

1.  The easiest way to test is to use the DrRecoveryWorkflowStateMachine.
    You can use the test event in tasks/extract_filepaths_for_granule/test/testevents/StepFunction.json.
    Edit the ['payload']['granules']['keys'] values as needed to be the file(s) you wish to restore.
    Edit the ['cumulus_meta']['execution_name'] to be something unique (like yyyymmdd_hhmm). Then
    copy and paste the same value to the execution name field above the input field.

2.  Execute the workflow. Once it passes the extract step, you can look at the output from it.


## Input
The lambda handler event excepts a dictionary having a list of granules as input. Check the input schema [here](https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/input.json) and the configuration schema [here](https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/config.json). An example input to the Lambda function can be seen below.
```
{
   "payload":{
      "granules":[
         {
            "granuleId":"MOD09GQ.A0219114.N5aUCG.006.0656338553321",
            "dataType":"MOD09GQ_test-jk2-IngestGranuleSuccess-1558420117156",
            "version":"006",
            "files":[
               {
                  "key":"MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5",
                  "bucket":"cumulus-test-sandbox-protected",
                  "fileName":"MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5",
                  "path":"jk2-IngestGranuleSuccess-1558420117156-test-data/files",
                  "url_path":"{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{extractYear(cmrMetadata.Granule.Temporal.RangeDateTime.BeginningDateTime)}/{substring(file.name, 0, 3)}",
                  "type":"data",
                  "duplicate_found":"True",
                  "size":1098034
               },
               {
                  "key":"MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.mp",
                  "bucket":"cumulus-test-sandbox-private",
                  "fileName":"MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.mp",
                  "path":"jk2-IngestGranuleSuccess-1558420117156-test-data/files",
                  "url_path":"{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}/{substring(file.name, 0, 3)}",
                  "type":"metadata",
                  "duplicate_found":"True",
                  "size":21708
               }
            ]
         }
   ]},
   "task_config":{
      "buckets": {
         "protected": {"name": "sndbx-cumulus-protected", "type": "protected"},
         "internal": {"name": "sndbx-cumulus-internal", "type": "internal"},
         "private": {"name": "sndbx-cumulus-private", "type": "private"},
         "public": {"name": "sndbx-cumulus-public", "type": "public"}
      },
      "fileBucketMaps":[
         {
            "regex":".*.h5$",
            "sampleFileName":"L0A_HR_RAW_product_0010-of-0420.h5",
            "bucket":"protected"
         },
         {
            "regex":".*.cmr.xml$",
            "sampleFileName":"L0A_HR_RAW_product_0010-of-0420.iso.xml",
            "bucket":"protected"
         },
         {
            "regex":".*.h5.mp$",
            "sampleFileName":"L0A_HR_RAW_product_0001-of-0019.h5.mp",
            "bucket":"public"
         },
         {
            "regex":".*.cmr.json$",
            "sampleFileName":"L0A_HR_RAW_product_0001-of-0019.cmr.json",
            "bucket":"public"
         }
      ],
      "excludeFileTypes":[
         ".cmr"
      ]
   }
}
```
## Output
The output of lambda handler returns a dictionary having a list of granules that consist of granuleID and keys with their destination buckets. Check the output schema example [here](https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/output.json).
```
{
   "granules":[
      {
         "granuleId":"MOD09GQ.A0219114.N5aUCG.006.0656338553321",
         "keys":[
            {
                "key": "MOD09GQ___006/2017/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5",
                "destBucket": "protected"
            },
            {
                "key": "MOD09GQ___006/MOD/MOD09GQ.A0219114.N5aUCG.006.0656338553321.h5.mp",
                "destBucket": "public"
            }
         ]
      }
   ]
}

```
## pydoc extract_filepaths_for_granule
[See the API documentation for more details.](API.md)