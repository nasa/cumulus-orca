## Description

The `copy_to_glacier_lambda` is meant to be deployed as a lambda function that takes a Cumulus message, extracts a list of files, and copies those files from their current storage location into a staging/glacier location.


## Build

The following steps assume you are using a current version of Python 3 (`pip` comes with current versions).

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt # requirements-dev.txt if you're testing/developing
```


## Test

This example uses `nose`, a package for testing Python projects.

```
# nose is installed as part of requirements-dev.txt
nosetests test
...
```


## Input

The `handler` function expects input as a Cumulus Message. The actual format of that input may change over time, so we use the `cumulus-process` package (check `requirements.txt`), which Cumulus develops and updates, to parse the input.

Example of expected [payload](https://nasa.github.io/cumulus/docs/workflows/input_output#5-resolve-task-output) to the task in a workflow:

```json
[
  "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
]
```

Example of expected input to the `handler` task itself:

```json
{
  "input": [
      "s3://ghrcsbxw-internal/file-staging/ghrcsbxw/goesrpltavirisng__1/goesrplt_avng_20170328t210208.tar.gz"
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
