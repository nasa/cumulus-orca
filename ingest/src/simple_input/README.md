# Simple Input Lambda

The `simple_input` lambda is a basic prototype meant to provide developers with a basic framework for the following items.

* Utilizing Poetry to manage their environment, dependency management, and packaging. More information at <https://python-poetry.org/docs/>
* Developing using a clean architecture approach that provides for an "adapter" to AWS lambda making the code more flexible to external changes. See <https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/> and <https://leanpub.com/clean-architectures-in-python>
* Providing automated unit testing for your application that not only tests the business logic but, provides ample coverage of your code for non-happy path implementations.
* Leveraging CI tools to maintain code quality through formatters, linters, and static code checkers.
* Building and packaging your code for a an AWS lambda function using Graviton processors
* Leveraging terraform to build the infrastructure to deploy your lambda to the cloud
* Leveraging Docker to not only build your code for AWS but for local testing
* Providing automation with git and Makefile commands.

## Development Environment

The following lays out developing for this prototype.

### Prerequisites

* VS Code
* Docker
* Python 3.11 or greater
* Development tools (make, cc, etc.)
* terraform 1.5 or greater
* curl
* jq

### Setting up

Once the repo is cloned `cd cumulus-orca/ingest/src/simple_input` and run `make setup`. This will do the following:

* Install poetry into your home directory
* Add the poetry-plugin-export
* Create a virtual environment for the project and install the needed libraries.

### Linting and formatting the code

To lint and format the code along with checking for code smell and possible third party CVE issues, run `make lint`.

Repair any issues before proceeding further.

### Testing the code

To test the code and receive a coverage report run `make test`.

Any test errors should be fixed. Coverage should be 98% or greater. If the value is low, additional unit tests should be created.

### Building the code for AWS deployment

To build the AWS lambda, layers, and IAC terraform code, run `make build-image`. This will create a dist folder with the proper artifacts.

The deployment can be tested by `cd dist/modules` and running `terraform init` and `terraform apply`. Do not forget to cleanup with `terraform destroy`.

### Testing the code locally

To test the code locally, run `make docker`. Once the docker container is running, issuing the following curl command should provide a successful return.

```bash
curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" -d @tests/events/test_event_success.json | jq
```

Note that the command uses the same input as the unit tests.

### Viewing the OpenAPI spec

To view the JSON OpenAPI spec run `make openapi`.

## TO DO

[] Fix API GW permissions to allow for calling the endpoint from EC2 instance
[] Determine how to populate the OpenAPI documentation from the Lambda
[] Update README with additional links and resources
[] Enhance prototype so that it interacts with AWS event bridge
[] Add .gitignore file and explain clean functionality.
[] Add method to stop test container
[] Add pre-commit and other items for automation with documentation
