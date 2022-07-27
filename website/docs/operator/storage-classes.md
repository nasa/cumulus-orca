---
id: storage-classes
title: S3 Storage Classes in Orca
description: Provides a brief overview on S3 storage classes available in Orca.
---

Orca can accept multiple [S3 storage classes](https://aws.amazon.com/s3/storage-classes/) on ingest.
These storage classes affect storage pricing, as well as available [retrieval options](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html).

See [Deployment With Cumulus](../developer/deployment-guide/deployment-with-cumulus.md) for details on choosing a default storage class and [Collection Configuration](collection-configuration.md) for setting the per-collection override value.

### GLACIER/Glacier Flexible Retrieval
This is Orca's default storage class. While the cost is higher, the retrieval time is significantly lower.

#### Retention
Each individual version is billed for a [minimum of 90 days of storage](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html#sc-glacier). 
As of the writing of this document, [the cost is .0036 per GB per month](https://aws.amazon.com/s3/pricing/).

#### Retrieval
Files stored in the `GLACIER` class can be recovered in as quickly as 5 minutes using the `Expedited` [option](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html) as needed. Cheaper options include the orca default `Standard` at 5 hours, and the Bulk at up to 12 hours. For pricing details, see 'Requests & data retrievals' on the [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/) page.

### DEEP_ARCHIVE

#### Retention
File versions stored in `DEEP_ARCHIVE` [cost roughly 1/3rd](https://aws.amazon.com/s3/pricing/) to keep stored in S3 compared to `GLACIER`,
and are billed for [double the `GLACIER` retention policy at 180 days](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html#sc-glacier).

`DEEP_ARCHIVE` is recommended for large files that will not see frequent changes.

# Retrieval
As a trade-off for their reduced cost compared to `GLACIER`, [`DEEP_ARCHIVE` retrieval takes 3-4 times as long](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html), and cannot be restored with the `Expedited` recovery type.
Retrieval also mildly increases in minimum [cost](https://aws.amazon.com/s3/pricing/) from the free `Bulk` tier in `GLACIER` to $0.0025 per GB.
