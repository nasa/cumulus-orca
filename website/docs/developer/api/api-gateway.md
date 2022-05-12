---
id: orca-api
title: ORCA API Reference
description: ORCA API reference for developers that provides API documentation and interactions.
---

## Overview

The purpose of this page is to give developers information on how to use the ORCA API and explain the expected inputs, outputs and paths. The API can be used to get metadata information about a granule, recovery job or to get information on internal reconciliation reports and accepts and responds with JSON payloads at various HTTPS endpoints. All ORCA APIs use the `POST` method.


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

| Name           | Data Type    | Description                                                                                                    | Required |
|----------------|--------------|----------------------------------------------------------------------------------------------------------------|----------|
| pageIndex      | `int`        | The 0-based index of the results page to return.                                                               | Yes      |
| endTimestamp   | `int`        | Cumulus granule createdAt end-time for date range to compare data, in milliseconds since 1 January 1970 UTC.   | Yes      |
| providerId     | `Array[str]` | The unique ID of the provider making the request.                                                              | No       |
| collectionId   | `Array[str]` | The unique ID of collection to compare.                                                                        | No       |
| granuleId      | `Array[str]` | The unique ID of granule to compare.                                                                           | No       |
| startTimestamp | `int`        | Cumulus granule createdAt start time for date range to compare data, in milliseconds since 1 January 1970 UTC. | No       |

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
          "hash": "ACFH325128030192834127347",
          "hashType": "SHA-256",
          "version": "VXCDEG902"
        }
      ]
    }
  ]
}
```
The following table lists the fields in the output:

| Name                   | Data Type       | Description                                                                                          |
|------------------------|-----------------|------------------------------------------------------------------------------------------------------|
| anotherPage            | `Boolean`       | Indicates if more results can be retrieved on another page.                                          |
| granules               | `Array[Object]` | A list of objects representing individual files to copy.                                             |
| providerId             | `int`           | The unique ID of the provider making the request.                                                    |
| collectionId           | `str`           | The unique ID of collection to compare.                                                              |
| id                     | `str`           | The unique ID of the granule.                                                                        |
| createdAt              | `int`           | The time, in milliseconds since 1 January 1970 UTC, data was originally ingested into cumulus.       |
| executionId            | `str`           | Step function execution ID from AWS.                                                                 |
| ingestDate             | `int`           | The time, in milliseconds since 1 January 1970 UTC, that the data was originally ingested into ORCA. |
| lastUpdate             | `int`           | The time, in milliseconds since 1 January 1970 UTC, that information was updated.                    |
| files                  | `Array[Object]` | Description and status of the files within the given granule.                                        |
| name                   | `str`           | The name and extension of the file.                                                                  |
| cumulusArchiveLocation | `str`           | Cumulus bucket the file resides in.                                                                  |
| orcaArchiveLocation    | `str`           | ORCA S3 Glacier bucket the file resides in.                                                          |
| keyPath                | `str`           | S3 path to the file including the file name and extension, but not the bucket.                       |
| sizeBytes              | `str`           | Size in bytes of the file. From Cumulus ingest.                                                      |
| hash                   | `str`           | Checksum hash of the file provided by Cumulus.                                                       |
| hashType               | `str`           | Hash type used to calculate the hash value of the file.                                              |
| version                | `str`           | AWS provided version of the file.                                                                    |


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

| Name             | Data Type | Description                                                                                | Required |
|------------------|-----------|--------------------------------------------------------------------------------------------|----------|
| granuleId        | `str`     | The unique ID of the granule to retrieve status for.                                       | Yes      |
| asyncOperationId | `str`     | The unique ID of the asyncOperation. May apply to a request that covers multiple granules. | No       |


### Recovery granules API output
An example of the API output is shown below:
```json
{
  "granuleId": "MOD14A1.061.H5V12.2020312.141531789",
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "files": [
    {
      "fileName": "f1.doc",
      "status": "pending"
    },
    {
      "fileName": "f2.pdf",
      "status": "failed",
      "error_message": "Access Denied"
    },
    {
      "fileName": "f3.txt",
      "status": "success"
    }
  ],
  "restoreDestination": "bucket_name",
  "requestTime": 628021800000,
  "completionTime": 628021900000
}

```

The following table lists the fields in the output:

| Name               | Data Type       | Description                                                                                                |
|--------------------|-----------------|------------------------------------------------------------------------------------------------------------|
| granuleId          | `str`           | The unique ID of the granule retrieved.                                                                    |
| asyncOperationId   | `str`           | The unique ID of the asyncOperation.                                                                       |
| files              | `Array[Object]` | Description and status of the files within the given granule.                                              |
| fileName           | `str`           | The name and extension of the file.                                                                        |
| status             | `str`           | The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.             |
| errorMessage       | `str`           | If the restoration of the file showed error, the error will be stored here.                                |
| restoreDestination | `str`           | The name of the glacier bucket the granule is being copied to.                                             |
| requestTime        | `int`           | The time, in milliseconds since 1 January 1970 UTC, when the request to restore the granule was initiated. |
| completionTime     | `int`           | The time, in milliseconds since 1 January 1970 UTC, when all granule_files were in an end state.           |

The API returns status code 200 on success, 400 if `granuleId` is missing, 500 if an error occurs when querying the database and 404 if not found.

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

| Name             | Data Type | Description                                              | Required |
|------------------|-----------|----------------------------------------------------------|----------|
| asyncOperationId | `str`     | The unique ID of the asyncOperation of the recovery job. | Yes      |


### Recovery jobs API output
An example of the API output is shown below:
```json
{
  "asyncOperationId": "43c9751b-9498-4733-90d8-56b1458e0f85",
  "jobStatusTotals": {
    "pending": 1,
    "success": 1,
    "failed": 1
  },
  "granules": [
    {
      "granuleId": "6c8d0c8b-4f9a-4d87-ab7c-480b185a0250",
      "status": "failed"
    },
    {
      "granuleId": "b5681dc1-48ba-4dc3-877d-1b5ad97e8276",
      "status": "pending"
    }
  ]
}
```
The following table lists the fields in the output:

| Name             | Data Type       | Description                                                                                                       |
|------------------|-----------------|-------------------------------------------------------------------------------------------------------------------|
| asyncOperationId | `str`           | The unique ID of the asyncOperation.                                                                              |
| jobStatusTotals  | `Object`        | Sum of how many granules are in each particular restoration status ('pending', 'staged', 'success', or 'failed'). |
| granules         | `Array[Object]` | An array representing each granule being copied as part of the job.                                               |
| granuleId        | `str`           | The unique ID of the granule retrieved.                                                                           |
| status           | `str`           | The status of the restoration of the file. May be 'pending', 'staged', 'success', or 'failed'.                    |

The API returns status code 200 on success, 400 if `asyncOperationId` is missing, 500 if an error occurs when querying the database and 404 if not found.

## Internal Reconcile report jobs API
The `orca/datamanagement/reconciliation/internal/jobs` API call receives page index from end user and returns available internal reconciliation jobs from the Orca database.
Internal reconcile report orphan API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/datamanagement/reconciliation/internal/jobs`

### Internal Reconcile report orphan API input
An example of the API input body is shown below:
```json
{
  "pageIndex": 0
}
```

The following table lists the fields in the input:

| Name             | Data Type | Description                                              | Required |
|------------------|-----------|----------------------------------------------------------|----------|
| pageIndex        | `int`     | The 0-based index of the results page to return.         | Yes      |


### Internal Reconcile report orphan API output
An example of the API output is shown below:
```json
{
  "anotherPage": false,
  "jobs": [
    {
      "id": 826,
      "orcaArchiveLocation": "PREFIX-orca-primary",
      "status": "success",
      "inventoryCreationTime": 1652227200000,
      "lastUpdate": 1652299312334,
      "errorMessage": null,
      "reportTotals": {
        "orphan": 0,
        "phantom": 1,
        "catalogMismatch": 1
      }
    },
    {
      "id": 793,
      "orcaArchiveLocation": "doctest-orca-primary",
      "status": "error",
      "inventoryCreationTime": 1652140800000,
      "lastUpdate": 1652198623479,
      "errorMessage": "Error while posting mismatches to database.",
      "reportTotals": {
        "orphan": 2,
        "phantom": 1,
        "catalogMismatch": 0
      }
    }
  ]
}
```
The following table lists the fields in the output:

| Name                  | Data Type       | Description                                                                                                   |
|-----------------------|-----------------|---------------------------------------------------------------------------------------------------------------|
| anotherPage           | `bool`          | Indicates if more results can be retrieved on another page.                                                   |
| jobs                  | `Array[Object]` | The jobs on the page.                                                                                         |
| id                    | `int`           | The unique ID of the reconciliation job.                                                                      |
| orcaArchiveLocation   | `str`           | ORCA S3 Glacier bucket the reconciliation targets.                                                            |           
| status                | `str`           | Current status of the job. `getting S3 list`, `staged`, `generating reports`, `error`, or `success`           |
| inventoryCreationTime | `int`           | The time, in milliseconds since 1 January 1970 UTC, of inventory report initiation time from the s3 manifest. |
| lastUpdate            | `int`           | The time, in milliseconds since 1 January 1970 UTC, when status was last updated.                             |
| errorMessage          | `str` or `null` | Critical error the job ran into that prevented it from finishing.                                             |
| reportTotals          | `Object`        | The number of error reports of each type.                                                                     |
| orphan                | `int`           | Number of files that have records in the S3 glacier bucket but are missing in the ORCA catalog.               |
| phantom               | `int`           | Number of files that have records in the ORCA catalog but are missing from S3 bucket.                         |
| catalogMismatch       | `int`           | Number of files that are missing from ORCA S3 bucket or have different metadata values than what is expected. |

The API returns status code 200 on success, 400 if `jobId` or `pageIndex` are missing and 500 if an error occurs.




## Internal Reconcile report orphan API
The `orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/orphans` API call receives job id and page index from end user and returns reporting information of files that have records in the S3 glacier bucket but are missing in the ORCA catalog from the internal reconciliation job. Note that `{jobid}` is optional.
Internal reconcile report orphan API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/orphans`

### Internal Reconcile report orphan API input
An example of the API input body is shown below:
```json
{
  "jobId": 123,
  "pageIndex": 0
}
```

The following table lists the fields in the input:

| Name             | Data Type | Description                                              | Required |
|------------------|-----------|----------------------------------------------------------|----------|
| jobId            | `int`     | The unique job ID of the reconciliation job.             | Yes      |
| pageIndex        | `int`     | The 0-based index of the results page to return.         | Yes      |


### Internal Reconcile report orphan API output
An example of the API output is shown below:
```json
{
  "jobId": 123,
  "anotherPage": false,
  "orphans": [
    {
      "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "s3Etag": "d41d8cd98f00b204e9800998ecf8427",
      "s3LastUpdate": "2020-01-01T23:00:00Z",
      "s3SizeInBytes": 6543277389,
      "storageClass": "glacier"
    }
  ]
}
```
The following table lists the fields in the output:

| Name             | Data Type       | Description                                                                 |
|------------------|-----------------|-----------------------------------------------------------------------------|
| jobId            | `str`           |The unique ID of the reconciliation job.                                     |
| anotherPage      | `Boolean`       | Indicates if more results can be retrieved on another page.                 |           
| orphans          | `Array[Object]` | An array representing each orphan if available.                             |
| s3SizeInBytes    | `int`           | Size in bytes of the object in S3 bucket.                                   |
| storageClass     | `str`           | AWS storage class the object is in the S3 bucket.                           |

The API returns status code 200 on success, 400 if `jobId` or `pageIndex` are missing and 500 if an error occurs.



## Internal Reconcile report phantom API
The `orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/phantoms` API call receives job id and page index from end user and returns reporting information of files that have records in the ORCA catalog but are missing from S3 bucket. Note that `{jobid}` is optional.
Internal reconcile report phantom API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/phantoms`

### Internal Reconcile report phantom API input
An example of the API input body is shown below:
```json
{
  "jobId": 123,
  "pageIndex": 0
}
```

The following table lists the fields in the input:

| Name             | Data Type | Description                                              | Required |
|------------------|-----------|----------------------------------------------------------|----------|
| jobId            | `int`     | The unique job ID of the reconciliation job.             | Yes      |
| pageIndex        | `int`     | The 0-based index of the results page to return.         | Yes      |


### Internal Reconcile report phantom API output
An example of the API output is shown below:
```json
{
  "jobId": 123,
  "anotherPage": false,
  "phantoms": [
    {
      "collectionId": "MOD09GQ___061",
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "filename": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "key_path": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "orcaEtag": "d41d8cd98f00b204e9800998ecf8427",
      "orcaLastUpdate": 628021970000,
      "orcaSize": 6543277389
    }
  ]
}
```
The following table lists the fields in the output:

| Name             | Data Type       | Description                                                                                                       |
|------------------|-----------------|-------------------------------------------------------------------------------------------------------------------|
| jobId            | `str`           |The unique ID of the reconciliation job.                                                                           |
| anotherPage      | `Boolean`       | Indicates if more results can be retrieved on another page.                                                       |       
| phantoms         | `Array[Object]` | An array representing each phantoms if available.                                                                 |
| collectionId     | `int`           | Cumulus Collection ID value from the ORCA catalog.                                                                |
| granuleId        | `str`           | Cumulus granuleID value from the ORCA catalog.                                                                    |
| filename         | `str`           | Filename of the object from the ORCA catalog.                                                                     |
| key_path         | `str`           | key path and filename of the object in the ORCA catalog.                                                          |  
| orcaEtag         | `str`           | etag of the object as reported in the ORCA catalog.                                                               |
| orcaLastUpdate   | `str`           | The time, in milliseconds since 1 January 1970 UTC, of last update of the object as reported in the ORCA catalog. |
| orcaSize         | `str`           | Size in bytes of the object as reported in the ORCA catalog.                                                      |

The API returns status code 200 on success, 400 if `jobId` or `pageIndex` are missing and 500 if an error occurs.

## Internal Reconcile report mismatch API
The `orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/mismatches` API call receives job id and page index from end user and returns reporting information of files that are missing from ORCA S3 bucket or have different metadata values than what is expected. Note that `{jobid}` is optional.
Internal reconcile report mismatch API input invoke URL example: `https://example.execute-api.us-west-2.amazonaws.com/orca/datamanagement/reconciliation/internal/jobs/job/{jobid}/mismatches`

### Internal Reconcile report mismatch API input
An example of the API input body is shown below:
```json
{
  "jobId": 123,
  "pageIndex": 0
}
```

The following table lists the fields in the input:

| Name             | Data Type | Description                                              | Required |
|------------------|-----------|----------------------------------------------------------|----------|
| jobId            | `int`     | The unique job ID of the reconciliation job.             | Yes      |
| pageIndex        | `int`     | The 0-based index of the results page to return.         | Yes      |


### Internal Reconcile report mismatch API output
An example of the API output is shown below:
```json
{
  "jobId": 123,
  "anotherPage": false,
  "mismatches": [
    {
      "collectionId": "MOD09GQ___061",
      "granuleId": "MOD09GQ.A2017025.h21v00.006.2017034065109",
      "filename": "MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "keyPath": "MOD09GQ/006/MOD09GQ.A2017025.h21v00.006.2017034065109.hdf",
      "cumulusArchiveLocation": "cumulus-public",
      "orcaEtag": "d41d8cd98f00b204e9800998ecf8427",
      "s3Etag": "1f78ve1d3f41vbhg4nbb4kjhong4x14",
      "orcaLastUpdate": "2020-01-01T23:00:00Z",
      "s3LastUpdate": "2020-01-01T23:00:00Z",
      "orcaSizeInBytes": 6543277389,
      "s3SizeInBytes": 1987618731,
      "discrepancyType": "etag, size_in_bytes",
      "comments": null
    }
  ]
}
```
The following table lists the fields in the output:

| Name             | Data Type       | Description                                                                                                       |
|------------------|-----------------|-------------------------------------------------------------------------------------------------------------------|
| jobId            | `str`           |The unique ID of the reconciliation job.                                                                           |
| anotherPage      | `Boolean`       | Indicates if more results can be retrieved on another page.                                                       |       
| mismatches       | `Array[Object]` | An array representing each mismatch if available.                                                                 |
| collectionId     | `int`           | Cumulus Collection ID value from the ORCA catalog.                                                                |
| granuleId        | `str`           | Cumulus granuleID value from the ORCA catalog.                                                                    |
| filename         | `str`           | Filename of the object from the ORCA catalog.                                                                     |
| keyPath          | `str`           | key path and filename of the object in the ORCA catalog.                                                          |
| cumulusArchiveLocation| `str`      | Expected S3 bucket the object is located in Cumulus. From the ORCA catalog.                                       |
| orcaEtag         | `str`           | etag of the object as reported in the ORCA catalog.                                                               |
| s3Etag           | `str`           | etag of the object as reported in the S3 bucket                                                                   |
| orcaLastUpdate   | `int`           | The time, in milliseconds since 1 January 1970 UTC, of last update of the object as reported in the ORCA catalog. |
| s3LastUpdate     | `int`           | The time, in milliseconds since 1 January 1970 UTC, that information was updated in the S3 bucket.                |
| orcaSizeInBytes  | `int`           | Size in bytes of the object as reported in the ORCA catalog.                                                      |
| s3SizeInBytes    | `int`           | Size in bytes of the object as reported in the S3 bucket.                                                         |
| discrepancyType  | `str`           | Type of discrepancy found during reconciliation.                                                                  |
| comment          | `str`           | Any additional context for the mismatch.                                                                          |

The API returns status code 200 on success, 400 if `jobId` or `pageIndex` are missing and 500 if an error occurs.