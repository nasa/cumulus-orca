[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_queue_and_trigger_step_function/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/post_to_queue_and_trigger_step_function/requirements.txt)

**Lambda function post_to_queue_and_trigger_step_function **

Receives an events from an SQS queue, sends it to another queue, then triggers an AWS step function.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [Input/Output Schemas](#input-output-schemas)
- [pydoc post_to_queue_and_trigger_step_function](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

<a name="pydoc"></a>
## pydoc post_to_queue_and_trigger_step_function
See API.md for documentation.