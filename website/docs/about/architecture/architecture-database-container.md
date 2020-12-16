---
id: architecture-database-container
title: Database Container Architecture
description: ORCA database schema information.
---

ORCA utilizes a single PostgreSQL RDBMS instance in AWS in order to track and
manage the status of a recovery in a typical recover data workflow. The diagram
below provides details on the access and schema used by ORCA to manage recovery
job status and tracking. The data within the database is considered transient
and is typically no longer useful after a recovery has reached completion in a
successful state.

![ORCA Database Container Context](../static/img/ORCA-Architecture-Database-Container-Component.svg)
