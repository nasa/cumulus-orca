[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_copy_request_to_queue/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/post_copy_request_to_queue/requirements.txt)

# Lambda function post_copy_request_to_queue

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input Schema and Example](#input-schema-and-example)
- [pydoc post_copy_request_to_queue](#pydoc-post_copy_request_to_queue)


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

## pydoc post_copy_request_to_queue
[See the API documentation for more details.](API.md)