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
      ],
      "config":{
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
```
Help on module extract_filepaths_for_granule:

NAME
    extract_filepaths_for_granule - Name: extract_filepaths_for_granule.py

DESCRIPTION
    Description:  Extracts the keys (filepaths) for a granule's files from a Cumulus Message.

CLASSES
    builtins.Exception(builtins.BaseException)
        ExtractFilePathsError
    
    class ExtractFilePathsError(builtins.Exception)
     |  Exception to be raised if any errors occur
     |  
     |  Method resolution order:
     |      ExtractFilePathsError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
     |  Data descriptors defined here:
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.Exception:
     |  
     |  __init__(self, /, *args, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |  
     |  __new__(*args, **kwargs) from builtins.type
     |      Create and return a new object.  See help(type) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |  
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |  
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |  
     |  __reduce__(...)
     |      Helper for pickle.
     |  
     |  __repr__(self, /)
     |      Return repr(self).
     |  
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |  
     |  __setstate__(...)
     |  
     |  __str__(self, /)
     |      Return str(self).
     |  
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |  
     |  __cause__
     |      exception cause
     |  
     |  __context__
     |      exception context
     |  
     |  __dict__
     |  
     |  __suppress_context__
     |  
     |  __traceback__
     |  
     |  args

FUNCTIONS
    get_regex_buckets(event)
        Gets a dict of regular expressions and the corresponding archive bucket for files
        matching the regex.
        
            Args:
                event (dict): passed through from the handler
        
            Returns:
                dict: dict containing regex and bucket.
        
            Raises:
                ExtractFilePathsError: An error occurred parsing the input.
    
    handler(event, context)
        Lambda handler. Extracts the key's for a granule from an input dict.
        
        Args:
            event (dict): A dict with the following keys:
        
                granules (list(dict)): A list of dict with the following keys:
                    granuleId (string): The id of a granule.
                    files (list(dict)): list of dict with the following keys:
                        key (string): The key of the file to be returned.
                        other dictionary keys may be included, but are not used.
                    other dictionary keys may be included, but are not used.
        
                Example: {
                            "event":{
                                "granules":[
                                    {
                                        "granuleId":"granxyz",
                                        "version":"006",
                                        "files":[
                                        {
                                            "fileName":"file1",
                                            "key":"key1",
                                            "source":"s3://dr-test-sandbox-protected/file1",
                                            "type":"metadata"
                                        }
                                        ]
                                    }
                                ]
                            }
                            }
        
            context (Object): None
        
        Returns:
            dict: A dict with the following keys:
        
                'granules' (list(dict)): list of dict with the following keys:
                    'granuleId' (string): The id of a granule.
                    'keys' (list(string)): list of keys for the granule.
        
            Example:
                {"granules": [{"granuleId": "granxyz",
                             "keys": ["key1",
                                           "key2"]}]}
        
        Raises:
            ExtractFilePathsError: An error occurred parsing the input.
    
    should_exclude_files_type(file_key: str, exclude_file_types: List[str]) -> bool
        Tests whether or not file is included in {excludeFileTypes} from copy to glacier.
        Args:
            file_key: The key of the file within the s3 bucket.
            exclude_file_types: List of extensions to exclude in the backup.
        Returns:
            True if file should be excluded from copy, False otherwise.
    
    task(event, context)
        Task called by the handler to perform the work.
        
        This task will parse the input, removing the granuleId and file keys for a granule.
        
            Args:
                event (dict): passed through from the handler
                context (Object): passed through from the handler
        
            Returns:
                dict: dict containing granuleId and keys. See handler for detail.
        
            Raises:
                ExtractFilePathsError: An error occurred parsing the input.

DATA
    CONFIG_EXCLUDE_FILE_TYPES_KEY = 'excludeFileTypes'
    CONFIG_FILE_BUCKETS_KEY = 'fileBucketMaps'
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    OUTPUT_DESTINATION_BUCKET_KEY = 'destBucket'
    OUTPUT_KEY_KEY = 'key'
```