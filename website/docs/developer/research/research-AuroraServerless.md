---
id: research-AuroraServerless
title: Aurora Serverless Research Notes
description: Research Notes on Aurora Serverless.
---

## Overview

[AWS Aurora Serverless](https://aws.amazon.com/rds/aurora/serverless/) is a resource used by other teams for storage with scaling architecture.
As part of our plans to utilize Cumulus' database for Orca storage, research was conducted to preemptively identify pitfalls and needed changes.
:::note
This page will not focus on moving to the database.
Instead, emphasis will be placed on connecting to and querying an already-unified Serverless database.
:::

### Implementation Details
- By default, Aurora scaling will only happen when no connections to the DB exist, but this can be overridden.
  :::note
  This means that if we do not handle connections responsibly or optimize our queries, we could hold up scaling operations for other teams.
  :::
- When scaling occurs, connections are cancelled, transactions are rolled back, locks are dropped, and temporary tables are dropped.
  :::note
  In our current technology, PostgreSQL, [each query is a transaction](https://www.postgresql.org/docs/8.3/tutorial-transactions.html). 
  :::
- When the Aurora DB is scaled down to zero, it takes some time to scale up.
  - With SQLAlchemy this translated to a 30-40 second hang on ```engine.begin()```
  - The default timeout for SQLAlchemy appears to be [30 seconds](https://docs.sqlalchemy.org/en/14/core/engines.html), though as mentioned previously connecting took 40 seconds with no issues.
    May be multiple timeouts in play.
  - Scaling up after this point did not cause query performance degradation, despite what was documented. However, the UI is poorly made, and may be reporting incorrectly.
- Connections canceled due to scaling raise an error in SQLAlchemy.
  If the query is ongoing:
  ```
  [SQL: 
  SELECT pg_sleep(600);
  ]
  (Background on this error at: http://sqlalche.me/e/14/e3q8)
  Traceback (most recent call last):
    File "...\venv\lib\site-packages\sqlalchemy\engine\base.py", line 1770, in _execute_context
      self.dialect.do_execute(
    File "...\venv\lib\site-packages\sqlalchemy\engine\default.py", line 717, in do_execute
      cursor.execute(statement, parameters)
  psycopg2.errors.AdminShutdown: terminating connection due to serverless scale event timeout
  SSL connection has been closed unexpectedly
  
  
  The above exception was the direct cause of the following exception:
  
  Traceback (most recent call last):
    File ".../main.py", line 85, in <module>
      connection.execute(wait_command)
      ...
  sqlalchemy.exc.OperationalError: (psycopg2.errors.AdminShutdown) terminating connection due to serverless scale event timeout
  SSL connection has been closed unexpectedly
  ```
  
  If the query is starting up:
  ```
  Database connection failed due to (psycopg2.OperationalError) FATAL:  terminating connection because backend initialization completed past serverless scale point
  
  (Background on this error at: https://sqlalche.me/e/14/e3q8)
  Traceback (most recent call last):
    ...
    File "...\venv\lib\site-packages\psycopg2\__init__.py", line 122, in connect
      conn = _connect(dsn, connection_factory=connection_factory, **kwasync)
  psycopg2.OperationalError: FATAL:  terminating connection because backend initialization completed past serverless scale point
  
  
  The above exception was the direct cause of the following exception:
  
  Traceback (most recent call last):
    File ".../main.py", line 84, in <module>
      with engine.begin() as connection:
    File "...\engine.py", line 393, in begin
      conn = self.connect()
    ...
  sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL:  terminating connection because backend initialization completed past serverless scale point
  
  (Background on this error at: https://sqlalche.me/e/14/e3q8)
  ```
  
  - Retrying when these errors occur should be sufficient to sidestep scaling errors, as scaling does not take long.
  :::warning
    Disconnections caused by these errors are NOT reported to Cloudwatch. Connecting lambdas/modules should have reliable and robust error logging.
  :::

### Future Direction
- Modifications should be made to database code to account for AdminShutdown, OperationalError, and connection timeout issues.
- Timeouts for Lambdas/code that use the database should account for the 30-40 second scale-up-time.
- Note that this code has not been tested with Lambdas.
  - [A SQLAlchemy plugin](https://pypi.org/project/sqlalchemy-serverless-aurora-plugin/) suggests that Lambdas "freeze" causing connection errors.
    - I question whether this actually matters more for Aurora Serverless compared to base Aurora.
    - Freeze only occurs after execution. Would be worth reviewing code to ensure connections do not live beyond lambda execution.

#### Sources
- [Best Practices for Working With Amazon Aurora Serverless](https://aws.amazon.com/blogs/database/best-practices-for-working-with-amazon-aurora-serverless/)
- [Aurora Serverless: How it Works](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless.how-it-works.html)