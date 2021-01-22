[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_glacier/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_glacier/requirements.txt)

Visit the [Developer Guide](../../website/docs/developer/development-guide/code/code-intro.md) for information on environment setup and testing.

## Description

The `copy_to_glacier` module is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.


## Exclude files by extension.

You are able to specify a list of file types (extensions) that you'd like to exclude from the backup/copy_to_glacier functionality. This is done on a per-collection basis, configured in the `meta` variable of a Cumulus collection configuration:

```json
{
  ...
  "meta": {
    "exclude_file_type": [".cmr", ".xml", ".cmr.xml"]
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

**Note:** We suggest that the `copy_to_glacier` task be placed any time after the `MoveGranulesStep`. It will propagate the input `granules` object as output, so it can be used as the last task in the workflow.


## Output

The copy lambda will, as the name suggests, copy a file from its current some source destination. The destination location is defined as 
`${glacier_bucket}/${filepath}`, where `${glacier_bucket}` is pulled from your Cumulus `meta.bucket` config and `${filepath}` is pulled from the Cumulus granule object input.

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

## pydoc request_files

```
NAME
    handler

FUNCTIONS
    copy_granule_between_buckets(source_bucket_name: str, source_key: str, destination_bucket: str, destination_key: str) -> None
        Copies granule from source bucket to destination.
        Args:
            source_bucket_name: The name of the bucket in which the granule is currently located.
            source_key: source Granule path excluding s3://[bucket]/
            destination_bucket: The name of the bucket the granule is to be copied to.
            destination_key: Destination granule path excluding s3://[bucket]/
    
    handler(event: Dict[str, Union[List[str], Dict]], context: object) -> Any
        Lambda handler. Runs a cumulus task that
        copies the files in {event}['input'] from the collection specified in {config} to the {config}'s 'glacier' bucket.
        
        Args:
            event: Event passed into the step from the aws workflow. A dict with the following keys:
                input (dict): Dictionary with the followig keys:
                    granules (List): List of granule objects (dictionaries)
                config (dict): A dict with the following keys:
                    collection (dict): The collection from AWS.
                        See https://nasa.github.io/cumulus/docs/data-cookbooks/sips-workflow
                        A dict with the following keys:
                        name (str): The name of the collection.
                            Used when generating the default value for {event}[config][fileStagingDir].
                        version (str): The version of the collection.
                            Used when generating the default value for {event}[config][fileStagingDir].
                        files (list[Dict]): A list of dicts representing file types within the collection.
                            The first file where the file's ['regex'] matches the filename from the input
                            Is used to identify the bucket referenced in return's['granules'][filename]['files']['bucket']
                            Each dict contains the following keys:
                                regex (str): The regex that all files in the bucket must match with their name.
                                bucket (str): The name of the bucket containing the files.
                        url_path (str): Used when calling {copy_granule_between_buckets} as a part of the destination_key.
                    buckets (dict): A dict with the following keys:
                        glacier (dict): A dict with the following keys:
                            name (str): The name of the bucket to copy to.
        
        
            context: An object required by AWS Lambda. Unused.
        
        Returns:
            The result of the cumulus task.
    
    should_exclude_files_type(granule_url: str, exclude_file_types: List[str]) -> bool
        Tests whether or not file is included in {excludeFileTypes} from copy to glacier.
        Args:
            granule_url: s3 url of granule.
            exclude_file_types: List of extensions to exclude in the backup
        Returns:
            True if file should be excluded from copy, False otherwise.
    
    task(event: Dict[str, Union[List[str], Dict]], context: object) -> Dict[str, Any]
        Copies the files in {event}['input'] from the collection specified in {config} to the {config}'s 'glacier' bucket.
        
        Args:
            event: Passed through from {handler}
            context: An object required by AWS Lambda. Unused.
        
        Returns:
            A dict with the following keys:
                granules (List[Dict[str, Union[str, bytes, list]]]): A list of dicts where each dict has the following keys:
                    granuleId (str): The filename from the granule url.
                    files (List): A list of dicts with the following keys:
                        name (str)
                        filename (str)
                        filepath (str)
                        bucket (str)
                copied_to_glacier (list): List of S3 paths - one for each file copied

```

