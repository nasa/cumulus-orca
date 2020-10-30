## Description

The `copy_to_glacier` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.


## Build

The following steps assume you are using a version of Python compliant with 3.7 (`pip` comes with current versions).

```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip       # Upgrade pip
pip install -r requirements.txt # requirements-dev.txt if you're testing/developing
```

An explicit example of building the lambda package can be found in `/bin/build_tasks.sh`.

## Deployment

Upload the zip file to AWS (either through the cli or console). Alternatively, `resources/lambdas/main.tf` shows an example of deploying this lambda through Terraform.

```
resource "aws_lambda_function" "copy_to_glacier" {
  function_name    = "${var.prefix}_copy_to_glacier"
  filename         = "${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip"
  source_code_hash = filemd5("${path.module}/../../tasks/copy_to_glacier/copy_to_glacier.zip")
  handler          = "handler.handler"
  role             = module.restore_object_arn.restore_object_role_arn
  runtime          = "python3.7"
  memory_size      = 2240
  timeout          = 600 # 10 minutes

  tags = local.default_tags
  environment {
    variables = {
      system_bucket               = var.buckets["internal"]["name"]
      stackName                   = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
    }
  }
```

## Testing & Linting

This example uses `pytest`, a package for testing Python projects.

```
# pytest and coverage are installed as part of requirements-dev.txt
coverage --source copy_to_glacier -m pytest # Run the tests
...
coverage report -m # Report the coverage stats
```

Manual integration testing is being worked on. TBD.

## Input

The `handler` function expects input as a Cumulus Message. The actual format of that input may change over time, so we use the `cumulus-process` package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

Example of expected [payload](https://nasa.github.io/cumulus/docs/workflows/input_output#5-resolve-task-output) to the task in a workflow:

```json
[
  "s3://testdaac-internal/file-staging/testdaac/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
]
```

Example of expected input to the `handler` task itself:

```json
{
  "input": [
      "s3://testdaac-internal/file-staging/testdaac/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
  ],
  "config": {
      "files_config": [
          {
              "regex": "^(.*).*\\.cmr.xml$",
              "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz.cmr.xml",
              "bucket": "public"
          },
          {
              "regex": "^(.*).*(\\.gz|\\.hdr|clip)$",
              "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz",
              "bucket": "protected"
          }
      ],
      "buckets": {
          "protected": {
              "type": "protected",
              "name": "testdaac-protected"
          },
          "internal": {
              "type": "internal",
              "name": "testdaac-internal"
          },
          "private": {
              "type": "private",
              "name": "testdaac-private"
          },
          "public": {
              "type": "public",
              "name": "testdaac-public"
          },
          "glacier": {
              "type": "private",
              "name": "testdaac-glacier"
          }
      },
      "collection": {
          "name": "goesrpltavirisng",
          "version": "1",
          "dataType": "goesrpltavirisng",
          "process": "metadataextractor",
          "provider_path": "/goesrpltavirisng/fieldCampaigns/goesrplt/AVIRIS-NG/data/",
          "url_path": "goesrpltavirisng__1",
          "duplicateHandling": "replace",
          "granuleId": "^goesrplt_avng_.*(\\.gz|\\.hdr|clip)$",
          "granuleIdExtraction": "^((goesrplt_avng_).*)",
          "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz",
          "files": [
              {
                  "bucket": "public",
                  "regex": "^goesrplt_avng_(.*).*\\.cmr.xml$",
                  "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz.cmr.xml"
              },
              {
                  "bucket": "protected",
                  "regex": "^goesrplt_avng_(.*).*(\\.gz|\\.hdr|clip)$",
                  "sampleFileName": "goesrplt_avng_20170323t184858.tar.gz"
              }
          ],
          "meta": {
              "metadata_extractor": [
                  {
                      "regex": "^(.*).*(\\.gz|\\.hdr|clip)$",
                      "module": "ascii"
                  }
              ],
              "granuleRecoveryWorkflow": "DrRecoveryWorkflow",
              "backupFileTypes": {}
          }}
  }
}
```

**Note:** According to the Cumulus documentation above, the output of the previous task (or a portion of it) is moved into the `input` key shown above. This means that the output of the task (in your workflow) leading up to this lambda function _must_ output the list of S3 file urls.

The following is an example of [Cumulus workflow configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration) for the `copy_to_glacier.handler` task:

```json
{
  "cma": {
    "event.$": "$",
    "ReplaceConfig": {
      "FullMessage": true
    },
    "task_config": {
      "collection": "{$.meta.collection}",
      "files_config": "{$.meta.collection.files}",
      "buckets": "{$.meta.buckets}",
      "cumulus_message": {
        "outputs": [ // Check Output documentation below for an explanation of this config.
          {
            "source": "{$}",
            "destination": "{$.payload}"
          }
        ]
      }
    }
  }
}
```

## Output

The copy lambda will, as the name suggests, copy a file from its current some source destination. The destination location is defined as 
`${glacier_bucket}/${url_path}/filename`, where `${glacier_bucket}` is pulled from your Cumulus `meta.bucket` config, `${url_path}` is pulled from the Cumulus `meta.collection` config, and `filename` is the base name of the file (with the file extension).

The output of this lambda is a dictionary with a `granules` and `input` attribute:

```json
{
	"granules": [
		{
			"granuleId": "goesrplt_avng_20170328t210208.tar.gz",
			"files": [
				{
					"path": "goesrpltavirisng__1",
					"url_path": "goesrpltavirisng__1",
					"bucket": "protected",
					"filename": "s3://testdaaac-internal/file-staging/testdaac/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz",
					"name": "s3://testdaac-internal/file-staging/testdaac/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
				}
			]
		}
	],
	"input": {
    ...
  }
}
```
