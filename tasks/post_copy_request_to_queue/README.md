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
        "eventVersion": "2.1",
        "eventSource": "aws:s3",
        "awsRegion": "us-west-2",
        "eventTime": "2019-09-03T19:37:27.192Z",
        "eventName": "ObjectRestore:Completed",
        "userIdentity": {
          "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
        },
        "requestParameters": {
          "sourceIPAddress": "205.255.255.255"
        },
        "responseElements": {
          "x-amz-request-id": "D82B88E5F771F645",
          "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
        },
        "s3": {
          "s3SchemaVersion": "1.0",
          "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
          "bucket": {
            "name": "orca-bucket",
            "ownerIdentity": {
              "principalId": "A3I5XTEXAMAI3E"
            },
            "arn": "arn:aws:s3:::orca-bucket"
          },
          "object": {
            "key": "f1.doc",
            "size": 1305107,
            "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
            "sequencer": "0C0F6F405D6ED209E1"
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
    handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]
        Lambda handler. Queries the DB and then posts to the recovery queue and DB queue.
        Args:
            event: A dict with the following keys:
                granule_id: The unique ID of the granule to retrieve status for.
                asyncOperationId (Optional): The unique ID of the asyncOperation.
            context: An object provided by AWS Lambda. Used for context tracking.
        
            Environment Vars:
                DATABASE_PORT (string): the database port. The standard is 5432.
                DATABASE_NAME (string): the name of the database.
                DATABASE_USER (string): the name of the application user.
                'PREFIX' (string): The prefix used in names. 
                OS_ENVIRON_DB_QUEUE_URL_KEY (string): The AWS SQS URL for the DB queue.
                OS_ENVIRON_RECOVERY_QUEUE_URL_KEY (string): The AWS SQS URL for the recovery queue.
```