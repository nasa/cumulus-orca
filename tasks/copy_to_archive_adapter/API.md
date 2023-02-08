# Table of Contents

* [copy\_to\_archive\_adapter](#copy_to_archive_adapter)
  * [task](#copy_to_archive_adapter.task)
  * [handler](#copy_to_archive_adapter.handler)

<a id="copy_to_archive_adapter"></a>

# copy\_to\_archive\_adapter

Name: copy_to_archive.py
Description: Lambda function that takes a Cumulus message, extracts a list of files,
and copies those files from their current storage location into a staging/archive location.

<a id="copy_to_archive_adapter.task"></a>

#### task

```python
def task(event: Dict[str, Union[List[str], Dict]],
         context: object) -> Dict[str, Any]
```

Converts event to a format accepted by ORCA's copy_to_archive lambda.

**Arguments**:

- `event` - Passed through from {handler}
- `context` - An object required by AWS Lambda. Unused.
  

**Returns**:

  A dict representing files to copy. See schemas/output.json for more information.

<a id="copy_to_archive_adapter.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[List[str], Dict]],
            context: LambdaContext) -> Any
```

Lambda handler. Runs a cumulus task that
Formats the input from the Cumulus format
to the format required by ORCA's copy_to_archive Lambda.

**Arguments**:

- `event` - Event passed into the step from the aws workflow.
  See schemas/input.json and schemas/config.json for more information.
  
  
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  

**Returns**:

  The result of the cumulus task. See schemas/output.json for more information.

