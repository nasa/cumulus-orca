---
id: orca-api
title: ORCA API Reference
description: ORCA API reference for developers that provides API documentation and interactions.
---

## Overview

The purpose of this page is to give developers information on how to use the ORCA API and explain the expected inputs, outputs and paths. The API can be used to get metadata information about a granule or a recovery job and accepts and responds with JSON payloads at various HTTPS endpoints. All ORCA APIs use the `POST` method.


## Catalog reporting API

The `catalog/reconcile` API call provides a user with the current listing of the ORCA catalog that can be used to reconcile granule and file information against a master catalog. For example, comparing the Cumulus primary archive holdings against the ORCA holdings to find discrepancies.
Catalog reporting API input invoke URL example:
`https://example.execute-api.us-west-2.amazonaws.com/orca/catalog/reconcile`

### Catalog reporting API input
An example of the API input body is shown below:
```json
{
  "pageIndex": 0,
  "providerId": ["lpdaac"],
  "collectionId": ["MOD14A1__061"],
  "granuleId": ["MOD14A1.061.A23V45.2020235"],
  "startTimestamp": "628021800000",
  "endTimestamp": "628021900000"
}
```
The following table lists the fields in the input:

| Name            | Data Type   | Description                                                                                                   | Required |
| ----------------| ------------|---------------------------------------------------------------------------------------------------------------|----------|
| pageIndex       | `int`       | The 0-based index of the results page to return.                                                              | Yes |
| endTimestamp   | `int`       | Cumulus granule createdAt end-time for date range to compare data, in milliseconds since 1 January 1970 UTC.  | Yes |
| providerId      | `Array[str]` | The unique ID of the provider making the request.                                                             | No  |
| collectionId    | `Array[str]` | The unique ID of collection to compare.                                                                       | No  |
| granuleId       | `Array[str]` | The unique ID of granule to compare.                                                                          | No  |
| startTimestamp  | `int`       | Cumulus granule createdAt start time for date range to compare data, in milliseconds since 1 January 1970 UTC.| No  |

### Catalog reporting API output
An example of the API output is shown below:
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
          "hash": "ACFH325128030192834127347"
          "hashType": "SHA-256",
          "version": "VXCDEG902"
        }
      ]
    }
  ]
}
```
The following table lists the fields in the output:

| Name                      | Data Type   |                           Description                                                               |
| --------------------------| ----------- | ----------------------------------------------------------------------------------------------------|
| anotherPage               | `Boolean`   | Indicates if more results can be retrieved on another page.                                         |
| granules                  | `Array[Object]`| A list of objects representing individual files to copy.                                         |
| providerId             | `int`       | The unique ID of the provider making the request.                                                   |
| collectionId           | `str`       | The unique ID of collection to compare.                                                             |
| id                     | `str`       | The unique ID of the granule.                                                                       |
| createdAt              | `int`       | The time, in milliseconds since 1 January 1970 UTC, data was originally ingested into cumulus.      |
| executionId            | `str`       | Step function execution ID from AWS.                                                                |
| ingestDate             | `int`       | The time, in milliseconds since 1 January 1970 UTC, that the data was originally ingested into ORCA.|
| lastUpdate             | `int`       | The time, in milliseconds since 1 January 1970 UTC, that information was updated.                   |
| files                  | `Array[Object]`| Description and status of the files within the given granule.                                    |
| name                   | `str`       | The name and extension of the file.                                                                 |
| cumulusArchiveLocation | `str`       | Cumulus bucket the file resides in.                                                                 |
| orcaArchiveLocation    | `str`       | ORCA S3 Glacier bucket the file resides in.                                                         |
| keyPath                | `str`       | S3 path to the file including the file name and extension, but not the bucket.                      |
| sizeBytes              | `str`       | Size in bytes of the file. From Cumulus ingest.                                                     |
| hash                   | `str`       | Checksum hash of the file provided by Cumulus.                                                      |
| hashType               | `str`       | Hash type used to calculate the hash value of the file.                                             |
| version                | `str`       | AWS provided version of the file.                                                                   |


The API returns status code 200 on success, 400 if `pageIndex` or  `endTimestamp` is missing and 500 if an error occurs when querying the database.

## Recovery granules API

The `recovery/granules` API call relates to an ORCA recovery job status and returns detailed status of the granule.

Recovery granules API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/recovery/granules`

### Recovery granules API input
An example of the API input body is shown below:
```json
{
  "granule_id": "MOD14A1.061.H5V12.2020312.141531789",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```
The following table lists the fields in the input:

| Name              | Data Type   | Description                                                                              | Required |
| ------------------|-------------|------------------------------------------------------------------------------------------|----------|
| granule_id        | `str`       | The unique ID of the granule to retrieve status for.                                     | Yes |
| asyncOperationId  | `str`       | The unique ID of the asyncOperation. May apply to a request that covers multiple granules. | No |


### Recovery granules API output
An example of the API output is shown below:
```json
{
  "granule_id": "MOD14A1.061.H5V12.2020312.141531789",
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

The following table lists the fields in the output:

| Name                   | Data Type  |                           Description                                                               |
| -----------------------| -----------| ----------------------------------------------------------------------------------------------------|
| granule_id            | `str`       | The unique ID of the granule retrieved.                                                             |
| asyncOperationId      | `str`       | The unique ID of the asyncOperation.                                                                |
| files                 | `Array[Object]`| Description and status of the files within the given granule.                                    |
| file_name          | `str`       | The name and extension of the file.                                                                 |
| status             | `str`       | The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.      |
| error_message         | `str`       | If the restoration of the file showed error, the error will be stored here.                         |
| restore_destination   | `str`       | The name of the glacier bucket the granule is being copied to.                                      |
| request_time          | `int`       | The time, in milliseconds since 1 January 1970 UTC, when the request to restore the granule was initiated.|
| completion_time       | `int`       | The time, in milliseconds since 1 January 1970 UTC, when all granule_files were in an end state.    |

The API returns status code 200 on success, 400 if `granule_id` is missing, 500 if an error occurs when querying the database and 404 if not found.

## Recovery jobs API
The `recovery/jobs` API call returns detailed status for a particular recovery job.
Recovery job API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/recovery/jobs`

### Recovery jobs API input
An example of the API input body is shown below:
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85"
}
```

The following table lists the fields in the input:

| Name              | Data Type   | Description                                               | Required |
| ------------------| ------------| ----------------------------------------------------------|-----------|
| asyncOperationId  | `str`       | The unique ID of the asyncOperation of the recovery job.  | Yes |


### Recovery jobs API output
An example of the API output is shown below:
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
The following table lists the fields in the output:

| Name                   | Data Type  |                           Description                                                               |
| -----------------------| -----------| ----------------------------------------------------------------------------------------------------|
| asyncOperationId      | `str`       | The unique ID of the asyncOperation.                                                                |
| job_status_totals     | `Object`    |Sum of how many granules are in each particular restoration status ('pending', 'staged', 'success', or 'failed').|
| granules              | `Array[Object]` | An array representing each granule being copied as part of the job.                                 |
| granule_id            | `str`       | The unique ID of the granule retrieved.                                                             |
| status                | `str`       | The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.      |

The API returns status code 200 on success, 400 if `asyncOperationId` is missing, 500 if an error occurs when querying the database and 404 if not found.
