---
id: unit-tests
title: Running Unit Tests
description: Instructions on running unit tests.
---

### Running Unit Tests and Coverage Checks
1. Navigate to the task's base folder.
1. Activate the virtual environment.
1. Run
    ```commandline
    coverage run --source [name of lambda] -m pytest
    ```
1. Output the coverage results to the file system by running
    ```commandline
    coverage html
    ```