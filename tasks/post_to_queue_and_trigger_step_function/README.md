[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_queue_and_trigger_step_function/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/post_to_queue_and_trigger_step_function/requirements.txt)

**Lambda function post_to_queue_and_trigger_step_function **

Receives an events from an SQS queue, translates to get_current_archive_list's input format,
sends it to another queue, then triggers the internal report step function.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas](#input-output-schemas)
- [pydoc post_to_queue_and_trigger_step_function](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
    "Records": 
    [
        {
            "body": "{\"Records\": [{\"awsRegion\": \"us-west-2\", \"s3\": {\"bucket\": {\"name\": \"PREFIX-orca-reports\"}, \"object\": {\"key\": \"PREFIX-orca-primary/PREFIX-orca-primary-inventory-report/2022-02-13T00-00Z/manifest.json\"}}}]}"
        }
    ]
}
```

<a name="pydoc"></a>
## pydoc post_to_queue_and_trigger_step_function
[See the API documentation for more details.](API.md)