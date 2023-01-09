---
id: research-logging-libraries
title: Logging Libraries Research Notes
description: Research notes on some potential logging libraries.
---

## Preconditions
- As ORCA runs in AWS, logger should tie into AWS structures.
- Presently, ORCA uses the [Python CumulusLogger](https://github.com/nasa/cumulus-message-adapter-python#logging-with-cumuluslogger).
- Presently, many ORCA tasks use `run_cumulus_task`, a related component of the Python CumulusLogger.

## CumulusLogger
- Developed by Cumulus for interactions with AWS and [CMA input/output](https://nasa.github.io/cumulus/docs/workflows/input_output).
- Adds some useful AWS context, though it is all redundant with information already stored in our CloudWatch logs, as long as we have one log-group per lambda.
- Tied to CMA-specific features such as [S3 storage of inputs](https://nasa.github.io/cumulus/docs/workflows/input_output#replaceconfig-cumulus-remote-message).
  - `run_cumulus_task` handles pulling in S3 events.
- Tied to CMA-specific [input/output](https://nasa.github.io/cumulus/docs/workflows/input_output#cma-inputoutput), which varies based on whether the running environment is AWS or Local.
- Maintained by/for Cumulus, which has caused conflicts with our development.
- Does not implement standard logging interface, requiring knowledge of the CumulusLogger-specific functions.

Example Cloudwatch message:
```
{
    "message": "some string",
    "sender": "lambda_name",
    "version": "$LATEST",
    "timestamp": "2022-09-02T18:06:00.782125",
    "level": "error"
}
```

Recommend we move away from CumulusLogger where possible.
The `ReplaceConfig` keys that would indicate use of the Logger's features are red-herrings, and the input formatting can be handled via standard AWS Step Function construction.
`copy_to_archive` is the one Lambda that Cumulus calls in their own workflows, and thus must be able to handle [S3 storage of inputs](https://nasa.github.io/cumulus/docs/workflows/input_output#replaceconfig-cumulus-remote-message).

## Default Logger
- Python's default [logging library](https://docs.python.org/3/library/logging.html) provides an excellent interface.
  Any proposed options should implement the standard library to maintain [clean architecture](./../development-guide/code/clean-architecture.mdx).
- Standard output is picked up by Lambda's Cloudwatch logs with no additional effort.
- Lacks information that would be helpful in determining AWS context unless added manually.

Code example:
```python
import json
import logging

LOGGER = logging.getLogger(__name__)

def lambda_handler(event, context):
    LOGGER.error("some string")
    return {
        'statusCode': 200,
        'body': json.dumps('results')
    }

```
Resulting Cloudwatch message:
`[ERROR]	2022-09-02T19:40:17.662Z	3020ae47-dd25-41b3-80fc-8bb3514cfb5c	some string`

## Powertools
- Available and documented on [AWSLabs](https://awslabs.github.io/aws-lambda-powertools-python/latest/).
- Implements Python's default [logging library](https://docs.python.org/3/library/logging.html).
- Requires environment variables for setup values.
- Automatically adds AWS context information.
- 

Code example:
```python
import json
import os

import aws_lambda_powertools
from aws_lambda_powertools.utilities.typing import LambdaContext

os.environ["POWERTOOLS_SERVICE_NAME"] = "powertools_test_service_name"
os.environ["LOG_LEVEL"] = "INFO"

LOGGER = aws_lambda_powertools.Logger()


def some_func():
    LOGGER.info("Doing thing.", extra={"someKey": 5})

    try:
        raise KeyError("some key error")
    except Exception as ex:
        LOGGER.exception("Auto logging")
        LOGGER.error(f"Manual logging: '{ex}'")
    return


@LOGGER.inject_lambda_context(log_event=True)  # event may be security risk
def lambda_handler(
        event, context: LambdaContext
):
    some_func()
    return {
        'statusCode': 200,
        'body': json.dumps('results')
    }
```

Resulting Cloudwatch message:
```
{
    "level": "ERROR",
    "location": "some_func:23",
    "message": "Manual logging: ''some key error''",
    "timestamp": "2022-09-01 20:11:25,278+0000",
    "service": "powertools_test_service_name",
    "cold_start": true,
    "function_name": "lambda_name",
    "function_memory_size": "128",
    "function_arn": "arn:aws:lambda:us-west-2:236859827343:function:lambda_name",
    "function_request_id": "bdb3bb29-5023-498a-b7a5-0582b03e215e",
    "xray_trace_id": "1-631111ec-64c294e313312cb53eb68777"
}
```

## Recommendation
- As the [Python CumulusLogger](https://github.com/nasa/cumulus-message-adapter-python#logging-with-cumuluslogger) is tied to Cumulus, 
  it is recommended that we decouple from it.
  - Any references to deployed layer should be removed from Terraform, including deployed layer and Step Function configuration.
  - Schema validation checks should be added to calling function.
  - References to run_cumulus_task should be replaced with manual transformation of inputs into non-architecture-specific formats.
    [Jira card for removal here](https://bugs.earthdata.nasa.gov/browse/ORCA-522).
  - `copy_to_archive` S3 requirements could be accomplished with a helper Lambda developed initially by us and maintained by Cumulus that handles the S3 retrieval 
    and passes the result along to `copy_to_archive`.
    [Jira card for implementation here](https://bugs.earthdata.nasa.gov/browse/ORCA-520).
- Given the standardized implementation and features of Powertools, it is a good pick for replacing the CumulusLogger in Orca code.
  [Jira card for replacement here](https://bugs.earthdata.nasa.gov/browse/ORCA-521).
- Recommend installing via Pip install as opposed to AWS Layer.
  [Documentation indicates](https://awslabs.github.io/aws-lambda-powertools-python/latest/core/logger/#removing-additional-keys) that there can be "unintended side effects if you use Layers" with certain features.
- Since Powertools properly implements the [standard Logging library](https://docs.python.org/3/library/logging.html), we can now use the `logging.exception` method to auto-capture and log exceptions, including stack traces.
  From the "Auto logging" code example above, Cloudwatch message is:
  ```
  {
      "level": "ERROR",
      "location": "some_func:22",
      "message": "Auto logging",
      "timestamp": "2022-09-01 20:11:25,278+0000",
      "service": "powertools_test_service_name",
      "cold_start": true,
      "function_name": "lambda_name",
      "function_memory_size": "128",
      "function_arn": "arn:aws:lambda:us-west-2:236859827343:function:lambda_name",
      "function_request_id": "bdb3bb29-5023-498a-b7a5-0582b03e215e",
      "exception": "Traceback (most recent call last):\n  File \"/var/task/powertools_test.py\", line 20, in some_func\n    raise KeyError(\"some key error\")\nKeyError: 'some key error'",
      "exception_name": "KeyError",
      "xray_trace_id": "1-631111ec-64c294e313312cb53eb68777"
  }
  ```
- Powertools also contains a [Tracing library](https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/) which could be helpful in debugging. Presently untested.
