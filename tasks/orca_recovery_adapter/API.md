# Table of Contents

* [orca\_recovery\_adapter](#orca_recovery_adapter)
  * [task](#orca_recovery_adapter.task)
  * [get\_state\_machine\_execution\_results](#orca_recovery_adapter.get_state_machine_execution_results)
  * [handler](#orca_recovery_adapter.handler)

<a id="orca_recovery_adapter"></a>

# orca\_recovery\_adapter

Name: orca_recovery_adapter.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and requests that those files be restored from ORCA.

<a id="orca_recovery_adapter.task"></a>

#### task

```python
def task(event: Dict[str, Union[List[str], Dict]],
         context: object) -> Dict[str, Any]
```

Converts event to a format accepted by ORCA's recovery step-function,
then calls step-function and returns the result.

**Arguments**:

- `event` - Passed through from {handler}
- `context` - An object required by AWS Lambda. Unused.
  
  Environment Variables:
  ORCA_RECOVERY_STEP_FUNCTION_ARN (string, required):
  ARN of ORCA's recovery step-function.
  

**Returns**:

  A dict representing input and copied files. See schemas/output.json for more information.

<a id="orca_recovery_adapter.get_state_machine_execution_results"></a>

#### get\_state\_machine\_execution\_results

```python
def get_state_machine_execution_results(client,
                                        execution_arn: str,
                                        retry_interval_seconds=5,
                                        maximum_duration_seconds=600) -> Dict
```

Synchronous running of step functions is not allowed via boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/start_sync_execution.html
so retry until it is complete.
Step function is relatively lightweight, so duration should be brief.

**Arguments**:

- `client` - The boto3 client to use when retrieving status.
- `execution_arn` - The AWS ARN of the step-function execution to monitor.
- `retry_interval_seconds` - How many seconds to wait between status retrievals.
- `maximum_duration_seconds` - The maximum duration of this function.
  If {retry_interval_seconds} would pass this limit, will return most recent status.
  

**Returns**:

  Step function execution results. If timeout was reached, status will be "RUNNING".

<a id="orca_recovery_adapter.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[List[str], Dict]],
            context: LambdaContext) -> Any
```

Lambda handler. Runs a cumulus task that
translates the input from the Cumulus format
to the format required by ORCA's recovery step-function,
then calls the recovery step-function and returns the result.

**Arguments**:

- `event` - Event passed into the step from the aws workflow.
  See schemas/input.json and schemas/config.json for more information.
  
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  
  Environment Variables:
  ORCA_RECOVERY_WORKFLOW_ARN (string, required):
  ARN of ORCA's recovery step function.
  

**Returns**:

  The result of the cumulus task. See schemas/output.json for more information.

