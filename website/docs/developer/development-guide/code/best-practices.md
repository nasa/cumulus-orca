---
id: best-practices
title: Best Practices
description: Best practices for coding in ORCA.
---

## Unit Testing
All code should reach minimum 80% coverage through [Unit Tests](unit-tests.md).

## Code Style
We use the [Google Style Guide](https://google.github.io/styleguide/pyguide.html) for style elements such as documentation, titling, and structure.

## Stop on Failure
Failures within ORCA should halt the Cumulus workflow they are a part of.
To this end, raising an error is preferred over catching the error and returning a null value or error message.

```python
try:
    value = function(param)
except requests_db.DatabaseError as err:
    logging.error(err)
    raise
```
```python
if not success:
    logging.error(f"You may log additional information if desired. "
                  f"param: {param}")
    raise DescriptiveErrorType(f'Error message to be raised info Cumulus workflow.'
```
:::note
Retrying a failing operation is perfectly acceptable so long as the number of retries is strictly limited.
You will likely want to log each individual error for analytics and debugging.
:::
