---
id: data-recovery
title: Data Recovery
description: Provides documentation for Operators to recover missing data.
---

import MyImage from '@site/docs/templates/pan-zoom-image.mdx';
import useBaseUrl from '@docusaurus/useBaseUrl';

:::important
As of ORCA v8.1 the Cumulus Message Adapter is no longer used. Users will need to deploy the recovery adapter before the recovery can be ran. Reference [Deployment with Cumulus](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment-with-cumulus#modify-the-recovery-workflow)
:::

## Recovery via Cumulus Dashboard

Recovery processes are kicked off manually by an operator through the Cumulus Dashboard. 
The dashboard calls an API which kicks off a recovery workflow.
Recovery is an asynchronous operation since data
requested from GLACIER can take 4 hours or more to reconstitute,
and DEEP_ARCHIVE can take 12 hours. 
Since it is asynchronous, the recovery container
relies on a database to maintain the status of the request and event
driven triggers to restore the data once it has been reconstituted
from archive into an S3 bucket. Currently, data is copied back to the
Cumulus S3 primary data bucket which is the default bucket. The operator 
has the option to override the default bucket with another restore bucket if desired. 
Determining the status of the recovery job is done manually by querying the database
directly or by checking the status on the dashboard.

A screenshot of the Cumulus dashboard used for recovering granules is shown below.

<img src={useBaseUrl('img/Cumulus-Dashboard-Recovery-Workflow.png')}
imageAlt="Cumulus Dashboard used for recovery"
zoomInPic={useBaseUrl('img/zoom-in.svg')}
zoomOutPic={useBaseUrl('img/zoom-out.svg')}
resetPic={useBaseUrl('img/zoom-pan-reset.svg')} />

On the dashboard home page, click on `Granules` option and add the granule to recover.
Then click on the `Options` button and select `Execute`. From the dropdown menu, 
select `OrcaRecoveryWorkflow` and hit `Confirm`. This will execute the recovery process.
There are several configurable parameters that can be set up while running the workflow and are explained in 
the section [below](#recovery-workflow-configurable-parameters).

## Manual recovery via step function workflow

An operator can also run the recovery by running the `Recovery Workflow` in step function. 

:::warning
The operator should have access to AWS console to manually run the workflow which is not ideal.
:::

### Recovery workflow input and output examples

The following is an input event example that an operator might set up while running the recovery workflow.

```json
{
  "payload": {
    "granules": [
      {
        "collectionId": "1234",
        "granuleId": "integrationGranuleId",
        "version": "integrationGranuleVersion",
        "files": [
          {
            "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
            "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
            "bucket": "test-orca-primary"
          }
        ]
      }
    ]
  },
  "meta": {
    "buckets": {
      "protected": {
        "name": "test-protected",
        "type": "protected"
      },
      "internal": {
        "name": "test-internal",
        "type": "internal"
      },
      "private": {
        "name": "test-private",
        "type": "private"
      },
      "public": {
        "name": "test-public",
        "type": "public"
      },
      "orca_default": {
        "name": "test-orca-primary",
        "type": "orca"
      }
    },
    "collection": {
      "meta": {
        "orca": {
          "excludedFileExtensions": [
            ".xml"
          ],
          "defaultBucketOverride": "test-orca-primary",
          "defaultRecoveryTypeOverride": "Standard"
        },
        "s3MultipartChunksizeMb": 200
      },
      "files": [
        {
          "regex": ".*.tar.gz",
          "sampleFileName": "blah.tar.gz",
          "bucket": "public"
        }
      ]
    }
  },
  "cumulus_meta": {
    "system_bucket": "test-internal",
    "asyncOperationId": "1234"
  }
}
```

The following is the corresponding output that the workflow will return if successful.

```json

{
  "granules": [
    {
      "collectionId": "integrationCollectionId",
      "granuleId": "integrationGranuleId",
      "version": "integrationGranuleVersion",
      "files": [
        {
          "fileName": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
          "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
          "bucket": "test-orca-primary"
        }
      ],
      "keys": [
        {
          "key": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
          "destBucket": "test-public"
        }
      ],
      "recoverFiles": [
        {
          "success": true,
          "filename": "MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
          "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065104.hdf",
          "restoreDestination": "test-public",
          "s3MultipartChunksizeMb": 200,
          "statusId": 1,
          "requestTime": "2022-11-16T17:29:19.008088+00:00",
          "lastUpdate": "2022-11-16T17:29:19.008088+00:00",
          "completionTime": "2022-11-16T17:29:19.008088+00:00"
        }
      ]
    }
  ],
  "asyncOperationId": "1234"
}

```

### Recovery workflow configurable parameters
The following are the parameters needed for recovery workflow:

- buckets- AWS S3 bucket mapping used for Cumulus and ORCA configuration. Contains the following properties:
  - name (Required)- Name of the S3 bucket.
  - type (Optional)- the type of bucket - i.e. internal, public, private, protected. 

  It can be set up using the following configuration.
  ```json
  "config": {
    "buckets.$": "$.meta.buckets"
  }
  ```
  Example:

  ```json
  "buckets": {
    "protected": {
      "name": "test-protected",
      "type": "protected"
    },
    "internal": {
      "name": "test-internal",
      "type": "internal"
    },
    "private": {
      "name": "test-private",
      "type": "private"
    },
    "public": {
      "name": "test-public",
      "type": "public"
    }
  }

  ```
- fileBucketMaps- A list of dictionaries that contains details of the configured storage bucket and file regex. Contains the following properties:
  - regex (Required)- The regex that matches the file extension type.
  - bucket (Required))- The name of the key that points to the correct S3 bucket. Examples include public, private, protected, etc.
  - sampleFileName (Optional)- name of a sample file having extension.

  It can be set up using the following configuration.
  ```json
  "config": {
    "fileBucketMaps.$": "$.meta.collection.files"
  }
  ```
  Example: 
  ```json
  "fileBucketMaps": [
    {
      "regex": ".*.h5$",
      "sampleFileName": "L0A_HR_RAW_product_0010-of-0420.h5",
      "bucket": "protected"
    },
    {
      "regex": ".*.cmr.xml$",
      "sampleFileName": "L0A_HR_RAW_product_0010-of-0420.cmr.xml",
      "bucket": "protected"
    }
  ]
  ```
- excludedFileExtensions (Optional)- A list of file extensions to ignore when copying files.
  It can be set up using the following configuration.
  ```json
  "config": {
    "excludedFileExtensions.$": "$.meta.collection.meta.orca.excludedFileExtensions"
  }
  ```
  Example: 
  ```json
  "collection": {
    "meta": {
      "orca": {
        "excludedFileExtensions": [
          ".xml"
        ]
      }
    }
  }
  ```
- defaultRecoveryTypeOverride (Optional)- Overrides the [orca_default_recovery_type](https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-optional-variables) via a change in the collections configuration under `meta` tag as shown below. 

  ```json
    "config": {
      "defaultRecoveryTypeOverride": "{$.event.meta.collection.meta.orca.defaultRecoveryTypeOverride}"
    }
  ```
  Example:
  ```json
      "collection": {
          "meta":{
              "orca": {
                "defaultRecoveryTypeOverride": "Standard"
            }
        }
      }
  ```
- defaultBucketOverride (Optional)- Overrides the [orca_default_bucket](https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-required-variables) to copy recovered files to.
  ```json
  "config": {
      "defaultBucketOverride": "{$.meta.collection.meta.orca.defaultBucketOverride}"
    }
  ```
  Example: 
  ```json
  "collection": {
    "meta": {
      "orca": {
        "defaultBucketOverride": "orca-bucket"
      }
    }
  }
  ```
- s3MultipartChunksizeMb (Optional)- Overrides the [default_multipart_chunksize_mb](https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/deployment-guide/deployment-with-cumulus.md#orca-optional-variables) from TF. Defaults to 250.
  ```json
  "config": {
    "s3MultipartChunksizeMb": "{$.meta.collection.meta.s3MultipartChunksizeMb}"
  }
  ```
  Example:
  ```json
  "collection": {
    "meta": {
      "s3MultipartChunksizeMb": 300
    }
  }
  ```

- asyncOperationId (Optional)- The unique identifier used for tracking requests. If not present, it will be generated.
  ```json
  "config": {
    "asyncOperationId": "{$.cumulus_meta.asyncOperationId}"
  }
  ```
  Example:
  ```json
  "cumulus_meta": {
    "asyncOperationId": "1234"
  }
  ```

For full definition of the parameters, see the following schema.
- [request_from_archive schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/request_from_archive/schemas/config.json)
- [extract_filepath_from_granule schema](https://github.com/nasa/cumulus-orca/blob/master/tasks/extract_filepaths_for_granule/schemas/config.json)