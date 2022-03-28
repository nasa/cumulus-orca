# Table of Contents

* [post\_to\_queue\_and\_trigger\_step\_function](#post_to_queue_and_trigger_step_function)
  * [process\_record](#post_to_queue_and_trigger_step_function.process_record)
  * [translate\_record\_body](#post_to_queue_and_trigger_step_function.translate_record_body)
  * [trigger\_step\_function](#post_to_queue_and_trigger_step_function.trigger_step_function)
  * [handler](#post_to_queue_and_trigger_step_function.handler)

<a id="post_to_queue_and_trigger_step_function"></a>

# post\_to\_queue\_and\_trigger\_step\_function

Name: post_to_queue_and_trigger_step_function.py

Description: Receives an events from an SQS queue, translates to get_current_archive_list's input format,
sends it to another queue, then triggers the internal report step function.

<a id="post_to_queue_and_trigger_step_function.process_record"></a>

#### process\_record

```python
def process_record(record: Dict[str, Any], target_queue_url: str,
                   step_function_arn: str) -> None
```

**Arguments**:

- `record` - The record to post.
- `target_queue_url` - The url of the queue to post the records to.
- `step_function_arn` - The arn of the step function to trigger.

<a id="post_to_queue_and_trigger_step_function.translate_record_body"></a>

#### translate\_record\_body

```python
def translate_record_body(body: str) -> Dict[str, Any]
```

Translates the SQS body into the format expected by the get_current_archive_list queue.

**Arguments**:

- `body` - The string to convert.
  

**Returns**:

  See get_current_archive_list/schemas/input.json for details.

<a id="post_to_queue_and_trigger_step_function.trigger_step_function"></a>

#### trigger\_step\_function

```python
@retry_error()
def trigger_step_function(step_function_arn: str) -> None
```

Triggers state machine with retries.

**Arguments**:

- `step_function_arn` - The arn of the step function to trigger.

<a id="post_to_queue_and_trigger_step_function.handler"></a>

#### handler

```python
def handler(event: Dict[str, Any], context) -> None
```

Lambda handler.
Receives an events from an SQS queue, translates to get_current_archive_list's input format,
sends it to another queue, then triggers the internal report step function.

**Arguments**:

- `event` - See input.json for details.
- `context` - An object passed through by AWS. Used for tracking.
  Environment Vars:
- `TARGET_QUEUE_URL` _string_ - The URL of the SQS queue the job came from.
- `Returns` - See output.json for details.

