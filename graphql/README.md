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
    When returning an `ExceptionGraphqlType` there should always be a `message` property 
    with a human-friendly explanation of the error.
- `resolvers` are called by `queries` or `mutations`.
- `queries` and `mutations` are standard GraphQL components, mapped to in the `graphql` package.
- `graphql` is run via the `webserver` package.

## Testing
### Local Testing
- Entry point is `src/adapters/webserver/main.py`, 
  which will start the developer UI at http://localhost:5000/graphql by default
  - Make sure to set the following environment variables:
    - `DB_CONNECT_INFO` = {"admin_database": "postgres", "admin_password": "{your admin password}", "admin_username": "postgres", "host": "localhost", "port": "5432", "user_database": "{PREFIX}_orca", "user_password": "{your user password}", "user_username": "{PREFIX}_orcauser"}
      - Replacing placeholders in `{brackets}` with proper values.
- If running via Docker
  - Set all environment variables in an `env` file.
    - Do NOT check this file into Github. Ideally, store this file outside the cloned repository.
  - Use the command `docker run -d -p 5000:5000 --env-file path/to/env imageName` 
    - Replace `imageName` with the name of your built image.
    - Replace `path/to/env` with the path to the env file you created in the previous step.
- The GraphQL URL is `http://localhost:5000/graphql`

### AWS Testing
1. If you wish to enable the developer GUI, add/modify the "ORCA_ENV" 
   in the `environment` section in your Terraform's `aws_ecs_task_definition` to
   ```json
   {
     "name": "ORCA_ENV",
     "value": "development"
   }
   ```
   then redeploy.

2. Get your `PREFIX-CumulusECSCluster` ec2 instance ID.
   This can be retrieved via the AWS GUI, or by running
   ```shell
   aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values={PREFIX}-CumulusECSCluster --query "Reservations[*].Instances[*].InstanceId" --output text
   ```
   replacing `{PREFIX}` with your prefix.

3. Run the following bash command, 
   replacing `i-00000000000000000` with your `PREFIX-CumulusECSCluster` ec2 instance ID.
   ```shell
   aws ssm pytest==6.2.5 --target i-00000000000000000 --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868
   ```
4. In a separate bash, run the following command,
   replacing `/blah/prefix.pem` with the path to your local `.pem` file for your installation and
   replacing `internal-PREFIX-gql-a-0000000000.us-west-2.elb.amazonaws.com` with the DNS name of your `PREFIX-gql-a` Application Load Balancer.
   ```shell
   ssh -p 6868 -L 5000:internal-PREFIX-gql-a-0000000000.us-west-2.elb.amazonaws.com:5000 -i "/blah/prefix.pem" -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1
   ```
5. The GraphQL URL is `http://localhost:5000/graphql`

### Test Code
- If the developer UI is enabled, you can access it at your GraphQL URL in a web browser.
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
  
  endpoint = "http://localhost:5000/graphql/"
  headers = {}
  
  r = requests.post(endpoint, json=json_body, headers=headers)
  if r.status_code == 200:
      print(json.dumps(r.json(), indent=2))
  else:
      raise Exception(f"Query failed to run with a {r.status_code}.")
  ```
  If needed, replace the `endpoint` with your GraphQL URL.

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
# todo: add recommendation to docs to ALWAYS request ErrorGraphqlTypeInterface with __typename and message properties

### Orca-Internal Schemas
todo

