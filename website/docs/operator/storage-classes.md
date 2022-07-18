---
id: storage-classes
title: S3 Storage Classes in Orca
description: Provides a brief overview on S3 storage classes available in Orca.
---

Orca can accept multiple [S3 storage classes](https://aws.amazon.com/s3/storage-classes/) on ingest.

See [Deployment With Cumulus](../developer/deployment-guide/deployment-with-cumulus.md) for details on choosing a default storage class and [Collection Configuration](collection-configuration.md) for setting the per-collection override value.

### GLACIER

### DEEP_ARCHIVE
Files stored in DEEP_ARCHIVE cannot be restored with the `Expedited` [recovery type](todo)
