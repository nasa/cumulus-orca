## Description

The `copy_to_glacier_lambda` is meant to be a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.


## Test

This example uses nose, a package for testing Python projects.
```
# Assuming you've followed the instructions in build and installed requirements-dev.txt
nosetests test
...
```


## Build

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt # requirements-dev.txt if you're testing/developing
```


## Input

The `handler` function expects input as a Cumulus Message. The actual format of that input may change over time, so we use the `cumulus-process` package (check `requirements.txt`), which Cumulus develops and updates, to parse the input for us.

Example of expected input to the task in a workflow:

```json
{
  "granules": [
    {
      "granuleId": "HLS.L30.T42WVU.2020272T065328.v1.5",
      "dataType": "HLSL30",
      "version": "1.5",
      "files": [
        {
          "name": "HLS.L30.T42WVU.2020272T065328.v1.5.B02.tif",
          "path": "L30/data/2020272/HLS.L30.T42WVU.2020272T065328.v1.5",
          "url_path": "HLSL30.015",
          "bucket": "lp-uat-protected",
          "size": 23674239,
          "checksumType": "SHA512",
          "checksum": "05cd7fe1b3e368d17a5b26428ecb9607c5aab02abf634a0834ea7be0c92e14cfa5629c4843b28a52bb3932dc33f0a910899f7f4bf1a53615a66f61a5b378e181",
          "type": "data",
          "filename": "s3://lp-uat-protected/HLSL30.015/HLS.L30.T42WVU.2020272T065328.v1.5.B02.tif",
          "filepath": "HLSL30.015/HLS.L30.T42WVU.2020272T065328.v1.5.B02.tif",
          "duplicate_found": true
        },
      ]
    }
  ]
}
```

Example of expected input to the `handler` task itself:

```json
{
  "input": {
      "granules": [
          {
              "files": [
                  {
                      "filename": "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
                  }
              ]
          }
      ]
  },
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
              "name": "ghrcsbxw-protected"
          },
          "internal": {
              "type": "internal",
              "name": "ghrcsbxw-internal"
          },
          "private": {
              "type": "private",
              "name": "ghrcsbxw-private"
          },
          "public": {
              "type": "public",
              "name": "ghrcsbxw-public"
          },
          "glacier": {
              "type": "private",
              "name": "ghrcsbxw-glacier"
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

cumulus message -> (CMA <- configuration) -> input to task

The following is an example of [Cumulus workflow configuration](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-configuration) for the `copy_to_glacier.handler` task:

```json
{
  "cma": {
    "event.$": "$",
    "ReplaceConfig": {
      "FullMessage": true
    },
    "task_config": {
      "backup_file_types": "{$.meta.collection.meta.backupFileTypes}",
      "collection": "{$.meta.collection}",
      "files_config": "{$.meta.collection.files}",
      "buckets": "{$.meta.buckets}",
      "cumulus_message": {
        "outputs": [ // Check Output documentation below for an explanation of this config.
          {
            "source": "{$.input.granules}",
            "destination": "{$.payload.granules}"
          },
          {
            "source": "{$.granules}",
            "destination": "{$.meta.glacier_files}"
          }
        ]
      }
    }
  }
}
```

## Output

The copy lambda will, as the name suggests, copy a file from its current source some destination. The destination location is defined as 
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
					"filename": "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz",
					"name": "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
				}
			]
		}
	],
	"input": {
    ...
  }
}
```
