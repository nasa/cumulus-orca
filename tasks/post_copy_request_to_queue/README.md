[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_copy_request_to_queue/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_files_to_archive/requirements.txt)

**Lambda function post_copy_request_to_queue **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input Schema and Example](#input-schema)
- [pydoc post_copy_request_to_queue](#pydoc)

<a name="input-schema"></a>
## Input Schema and Example
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
Input coming from ORCA S3 bucket trigger event.
```json
{
    "Records": [
      {
        "eventSource": "aws:s3",
        "eventName": "ObjectRestore:Completed",
        "s3": {
          "bucket": {
            "name": "orca-bucket",
            "arn": "arn:aws:s3:::orca-bucket"
          },
          "object": {
            "key": "f1.doc",
          }
        }
      }
    ]
  }
```

<a name="pydoc"></a>
## pydoc post_copy_request_to_queue
```
Help on module post_copy_request_to_queue:

NAME
    post_copy_request_to_queue

FUNCTIONS
    handler(event: Dict[str, Any], context: None) -> None
        Lambda handler. Queries the DB and then posts to the recovery queue and DB queue.
        Args:
            event: A dictionary coming from the S3 bucket trigger event. See schemas/input.json for more information.
            context: An object provided by AWS Lambda. Unused.
        
          Environment Vars:
              PREFIX (string): the prefix
              DATABASE_PORT (string): the database port. The standard is 5432.
              DATABASE_NAME (string): the name of the database.
              DATABASE_USER (string): the name of the application user.
              DB_QUEUE_URL (string): the SQS URL for status-update-queue
              RECOVERY_QUEUE_URL (string): the SQS URL for staged_recovery_queue
          Parameter store:
              {prefix}-drdb-host (string): host name that will be retrieved from secrets manager
              {prefix}-drdb-user-pass (string):db password that will be retrieved from secrets manager
        Returns:
          None
        Raises:
          Exception: If unable to retrieve the SQS URLs or exponential retry fields from env variables.

    exponential_delay(base_delay: int, exponential_backoff: int) -> int:
        Exponential delay function. This function is used for retries during failure.
        Args:
            base_delay: Number of seconds to wait between recovery failure retries.
            exponential_backoff: The multiplier by which the retry interval increases during each attempt.
        Returns:
            An integer which is multiplication of base_delay and exponential_backoff.
        Raises:
            None
    task(records: List[Dict[str, Any]], db_queue_url: str, recovery_queue_url: str, max_retries: int, retry_sleep_secs: int retry_backoff: int,) -> None:
        Task called by the handler to perform the work. This task queries all entries from orca_recoverfile table that match the given filename and whose status_id is 'PENDING'. The result is then sent to the staged-recovery-queue SQS and status-update-queue SQS.

      Args:
          records: A list of dictionary passed through from the handler.
          db_queue_url: The SQS URL of status_update_queue
          recovery_queue_url: The SQS URL of staged_recovery_queue
          max_retries: Number of times the code will retry in case of failure.
          retry_sleep_secs: Number of seconds to wait between recovery failure retries.
          retry_backoff: The multiplier by which the retry interval increases during each attempt.
      Returns:
          None
      Raises:
          Exception: If unable to retrieve key_path or db parameters, convert db result to json,
          or post to queue.
```