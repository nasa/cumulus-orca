---
id: linting
title: Running PyLint Against Your Code
description: Instructions on running PyLint.
---

### Running PyLint
```
Run pylint against the code:

(podr) λ cd C:\devpy\poswotdr\tasks\copy_files_to_archive
(podr) λ pylint copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_copy_files_to_archive.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

(podr) λ pylint test/test_copy_files_to_archive_postgres.py
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```