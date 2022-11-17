[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=graphql/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=graphql/requirements.txt)

**GraphQL Application**

Handles database queries for ORCA applications and users.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Development](#development)
- [Local Testing](#local-testing)
- [Deployment](#deployment)
- [Schemas](#schemas)

## Development
- Isolate business logic in `use_cases`, returning an `entity`.
- `adapter` classes are initialized in `initialized_adapters`.
- `resolvers` calls the `use_case`, passing in `initialized_adapters` as needed.
- Objects returned by GraphQL require decorators such as `@strawberry.type` and `@strawberry.enum`
  - Due to complications in adhering to strict 
    [Clean Architecture](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/clean-architecture)
    it may be beneficial to apply GraphQL decorators at the entity layer.
    Since this means that GraphQL will return these entities, 
    make sure they do not contain any fields that clients should not see.
  - `resolvers` should catch and convert any exceptions to `dataTypes`.
    When returning an `ExceptionStrawberryType` there should always be a `message` property 
    with a human-friendly explanation of the error.
- `resolvers` are called by `queries` or `mutations`.
- `queries` and `mutations` are standard GraphQL components, mapped to in the `graphql` package.
- `graphql` is run via the `webserver` package.

## Local Testing
- Entry point is `src/adapters/webserver/main.py`, 
  which will start the developer UI at http://127.0.0.1:5000/graphql by default
  - Make sure to set the following environment variables:
    - `ADMIN_PASSWORD`
    - `DATABASE_HOST`
    - `DATABASE_PORT`
    - `USER_DATABASE_NAME`
    - `USER_USERNAME`
    - `APPLICATION_PASSWORD`
    - `RUNNING_LOCALLY=True`
- If running via Docker
  - Set all environment variables in an `env` file.
    - Do NOT check this file into Github. Ideally, store this file outside the cloned repository.
  - Use the command `docker run -d -p 5000:5000 --env-file path/to/env imageName` 
    - Replace `imageName` with the name of your built image.
    - Replace `path/to/env` with the path to the env file you created in the previous step.
- If using the developer UI, queries can be converted to code-friendly representations using the following code:
  ```python
  query = """query {
    getEcho {
      ... on EchoEdge {
        node {
          echo
        }
      }
    }
  }"""
  json_body = {"query": query}
  
  print(json_body)
  ```
  
- These queries can be run against an available instance with the following Python code:
  ```python
  import json
  import requests
  
  endpoint = "http://0.0.0.0:5000/graphql/"
  headers = {}
  
  r = requests.post(endpoint, json=json_body, headers=headers)
  if r.status_code == 200:
      print(json.dumps(r.json(), indent=2))
  else:
      raise Exception(f"Query failed to run with a {r.status_code}.")
  ```

## Deployment
Compiled packages are stored at the [NASA Github packages page](https://github.com/orgs/nasa/packages/container/package/cumulus-orca%2Fgraphql).
Once a new version is ready for deployment, perform the following steps:
1. Choose a new version number following [semantic versioning practices](https://semver.org/).
1. From the root `graphql` folder, run
   ```bash
   bin/create_and_push_docker_image.sh $version_number $github_access_token
   ```
   - `$version_number` is the version number from the previous step.
   - `$github_access_token` is an [access token](https://github.com/settings/tokens) with the `write:packages` permission, created for a user with access to the NASA account.
1. Update the `image` property in the [GraphQL Terraform module](https://github.com/nasa/cumulus-orca/blob/master/modules/graph_ql/main.tf) with your new version number.
1. Your new GraphQL version will now be deployed on `terraform apply`.

### Environment Variables
- HOST
- PORT
- ORCA_ENV: Set to `development` to enable dev-only features such as query-builder GUI and allowing queries via `GET`.
  

<a name="input-output-schemas"></a>
## Schemas
### Customer-Accessible Schemas
See [ORCA API Reference](https://nasa.github.io/cumulus-orca/docs/developer/api/orca-api) 
for customer-centric API documentation.
# todo: add recommendation to docs to ALWAYS request ErrorStrawberryTypeInterface with __typename and message properties

### Orca-Internal Schemas
todo

