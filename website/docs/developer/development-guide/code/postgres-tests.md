---
id: postgres-tests
title: Running Postgres Tests
description: Instructions on running 'postgres' tests.
---

## Preparing to Run Postgres Tests
Test files ending in '_postgres.py' require a postgres database to be accessible.

1. Make sure you have Docker running on your machine.
1. Open a command prompt and run
    ```commandline
    docker run -it --rm --name some-postgres -v [path to repository]/database/ddl/base:/docker-entrypoint-initdb.d/ -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
    ```
1. The running database can now be accessed at localhost:5432
1. Use the username and password 'postgres' to access it and set the password for 'druser'.
    ```commandline
    docker run -it --rm --network host -e POSTGRES_PASSWORD=[your password here] postgres psql -h localhost -U postgres`
    ```
1. Place a file called 'private_config.json' in the postgres' test folder and give it the information for your database.
    ```json
    {"DATABASE_HOST": "localhost",
    "DATABASE_PORT": "5432",
    "DATABASE_NAME": "disaster_recovery",
    "DATABASE_USER": "druser",
    "DATABASE_PW": "[your password here]",
    "MASTER_USER_PW": "postgres"}
    ```
   These values will be injected into your environment variables before the test is run.
1. You may now run postgres tests the same way you would [unit tests](unit-tests).