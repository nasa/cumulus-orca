# Table of Contents

* [post\_to\_queue\_and\_trigger\_step\_function](#post_to_queue_and_trigger_step_function)
  * [process\_record](#post_to_queue_and_trigger_step_function.process_record)
  * [translate\_record\_body](#post_to_queue_and_trigger_step_function.translate_record_body)
  * [trigger\_step\_function](#post_to_queue_and_trigger_step_function.trigger_step_function)
  * [handler](#post_to_queue_and_trigger_step_function.handler)
* [sqs\_library](#sqs_library)
  * [retry\_error](#sqs_library.retry_error)
  * [post\_to\_fifo\_queue](#sqs_library.post_to_fifo_queue)

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

Central method for translating record to pass along and triggering step function.

**Arguments**:

- `record` - The record to post. See schemas/input.json under Records/items for details.
- `target_queue_url` - The url of the queue to post the records to.
- `step_function_arn` - The arn of the step function to trigger.

<a id="post_to_queue_and_trigger_step_function.translate_record_body"></a>

#### translate\_record\_body

```python
def translate_record_body(s3_record: Dict[str, Any]) -> Dict[str, Any]
```

Translates the s3 body into the format expected by the get_current_archive_list queue.

**Arguments**:

- `s3_record` - See schemas/body.json under Records/items for details.
  

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

<a id="sqs_library"></a>

# sqs\_library

Name: sqs_library.py
Description: library for post_to_queue_and_trigger_step_function lambda function for posting to fifo SQS queue.
Largely copied from copy_to_glacier

<a id="sqs_library.retry_error"></a>

#### retry\_error

```python
def retry_error(
    max_retries: int = MAX_RETRIES,
    backoff_in_seconds: int = INITIAL_BACKOFF_IN_SECONDS,
    backoff_factor: int = BACKOFF_FACTOR
) -> Callable[[Callable[[], RT]], Callable[[], RT]]
```

Decorator takes arguments to adjust number of retries and backoff strategy.

**Arguments**:

- `max_retries` _int_ - number of times to retry in case of failure.
- `backoff_in_seconds` _int_ - Number of seconds to sleep the first time through.
- `backoff_factor` _int_ - Value of the factor used for backoff.

<a id="sqs_library.post_to_fifo_queue"></a>

#### post\_to\_fifo\_queue

```python
@retry_error()
def post_to_fifo_queue(queue_url: str, sqs_body: Dict[str, Any]) -> None
```

Posts information to the given SQS queue.

**Arguments**:

- `sqs_body` - A dictionary containing the objects that will be sent to SQS.
- `queue_url` - The SQS queue URL defined by AWS.

**Raises**:

  None

