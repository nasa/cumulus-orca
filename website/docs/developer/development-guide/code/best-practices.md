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
Failures within ORCA break through to the Cumulus workflow they are a part of.
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
In the event that an error is likely transient, and failing would cause a large amount of redundant work for other objects, retrying a failing operation in code is acceptable with a strictly limited number of retries.
You will likely want to log each individual error for analytics and debugging.
:::
The Cumulus Workflow [can be configured](https://aws.amazon.com/getting-started/hands-on/handle-serverless-application-errors-step-functions-lambda/) with retries or stop-on-failure.
