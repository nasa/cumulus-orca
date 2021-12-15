---
id: API gateway paths, inputs and outputs
title: API Gateway paths, inputs and outputs
description: Additional notes on API gateway paths, inputs and expected outputs.
---

## Overview

This documentation provides details on the paths, input and outputs for the `orca_api` API gateway. The format for the API invoke URL is `https://example.execute-api.us-west-2.amazonaws.com/[stage_name]/[path]`. Check [API gateway research webpage](https://github.com/nasa/cumulus-orca/blob/master/website/docs/developer/research/research-APIGateway.md) for more information.

## Path 
- The path `catalog/reconcile` of `orca_api` API gateway returns additional metadata information needed for reporting by triggering the `orca_catalog_reporting` lambda.
- The path `recovery/granules` of `orca_api` API gateway returns detailed status of the granule by triggering the `request_status_for_granule` lambda.
- The path `recovery/jobs` of `orca_api` API gateway returns detailed status for a particular recovery job by triggering the `request_status_for_job` lambda.

### Inputs and outputs
The API invoke URL can be found under `Stages` section in API gateway UI. All APIs use the `POST` method.

- Catalog reporting API invoke URL example:
`https://example.execute-api.us-west-2.amazonaws.com/orca/catalog/reconcile`

- Catalog reporting API output example:
```json
{
  "anotherPage": false,
  "granules": [
    {
      "providerId": "lpdaac",
      "collectionId": "MOD14A1___061",
      "id": "MOD14A1.061.A23V45.2020235",
      "createdAt": "628021850000",
      "executionId": "u654-123-Yx679",
      "ingestDate": "628021950000",
      "lastUpdate": "628021970000",
      "files": [
        {
          "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
          "cumulusArchiveLocation": "cumulus-bucket",
          "orcaArchiveLocation": "orca-archive",
          "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
          "sizeBytes": 100934568723,
          "hash": "ACFH325128030192834127347",
          "hashType": "SHA-256",
          "version": "VXCDEG902"
        }
      ]
    }
  ]
}

```

- Recovery granules invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/recovery/granules`

- Recovery granules API output example:
```json
{
  "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "file_name": "f1.doc",
      "status": "pending"
    },
    {
      "file_name": "f2.pdf",
      "status": "failed",
      "error_message": "Access Denied"
    },
    {
      "file_name": "f3.txt",
      "status": "success"
    }
  ],
  "restore_destination": "bucket_name",
  "request_time": 628021800000,
  "completion_time": 628021900000
}

```

- Recovery job API invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/recovery/jobs`

- Recovery job API output example:
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "job_status_totals": {
    "pending": 1,
    "success": 1,
    "failed": 1
  },
  "granules": [
    {
      "granule_id": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
      "status": "failed"
    },
    {
      "granule_id": "b5681dc1-48ba-4dc3-877d-1b5ad97e8276",
      "status": "pending"
    }
  ]
}

```