## Description

The `copy_to_glacier` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.


## Excluding certain file extensions from the copy

You are able to specify a list of file types (extensions) that you'd like to exclude from the backup/copy_to_glacier functionality. This is done on a per-collection basis, configured in the `meta` variable of a Cumulus collection configuration:

```json
{
  ...
  "meta": {
    "exclue_file_type": [".cmr", ".xml", ".cmr.xml"]
  }
}
```

Note that this must be done for _each_ collection configured. If this list is empty or not included in the meta configuration, the `copy_to_glacier` function will include files with all extensions in the backup.


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

Upload the zip file to AWS (either through the cli or console). Alternatively, `modules/lambdas/main.tf` shows an example of deploying this lambda through Terraform.

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
coverage run --source copy_to_glacier -m pytest # Run the tests
...
coverage report -m # Report the coverage stats
```

Manual integration testing is being worked on. TBD.

## Input

The `handler` function expects input as a Cumulus Message. The actual format of that input may change over time, so we use the `cumulus-process` package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

The `copy_to_glacier` lambda function expects that the input payload has a `granules` object, similar to the output of `MoveGranulesStep`:

```json
{
  "payload": {
    "granules": [
      {
        "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
        "dataType": "MOD09GQ",
        "version": "006",
        "files": [
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318361000,
            "bucket": "orca-sandbox-protected",
            "url_path": "MOD09GQ/006/",
            "type": "",
            "filename": "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318366000,
            "bucket": "orca-sandbox-private",
            "url_path": "MOD09GQ/006",
            "type": "",
            "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "path": "MOD09GQ/006",
            "size": 6,
            "time": 1608318372000,
            "bucket": "orca-sandbox-public",
            "url_path": "MOD09GQ/006",
            "type": "",
            "filename": "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
            "duplicate_found": true
          },
          {
            "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "bucket": "orca-sandbox-private",
            "filename": "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "type": "metadata",
            "filepath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml",
            "url_path": "MOD09GQ/006"
          }
        ],
        "sync_granule_duration": 1728
      }
    ]
  }
}
```

## Output

The copy lambda will, as the name suggests, copy a file from its current some source destination. The destination location is defined as 
`${glacier_bucket}/${url_path}/filename`, where `${glacier_bucket}` is pulled from your Cumulus `meta.bucket` config, `${url_path}` is pulled from the Cumulus `meta.collection` config, and `filename` is the base name of the file (with the file extension).

The output of this lambda is a dictionary with a `granules` and `copied_to_glacier` attributes:

```json
{
	"granules": [
    {
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "dataType": "MOD09GQ",
      "version": "006",
      "files": [
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318361000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006/",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        },
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318366000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        },
        {
          "name": "MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
          "path": "MOD09GQ/006",
          "size": 6,
          "time": 1608318372000,
          "bucket": "orca-sandbox-internal",
          "url_path": "MOD09GQ/006",
          "type": "",
          "filename": "s3://orca-sandbox-internal/file-staging/orca-sandbox/MOD09GQ___006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
          "fileStagingDir": "file-staging/orca-sandbox/MOD09GQ___006"
        }
      ],
      "sync_granule_duration": 1676
    }
  ],
	"copied_to_glacier": [
      "s3://orca-sandbox-protected/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf.met",
      "s3://orca-sandbox-public/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109_ndvi.jpg",
      "s3://orca-sandbox-private/MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.cmr.xml"
  ]
}
```
