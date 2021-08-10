---
id: research-graphql
title: GraphQL Research Notes
description: Research Notes on GraphQL.
---

## Overview

[GraphQL](https://graphql.org/) is an open-source data query and manipulation language for APIs, and a runtime for fulfilling queries with existing data.

 - A GraphQL server provides a client with a predefined schema written down in Schema Definition Language (SDL). 
 - The schema defines the queries that can be made.
 - The SDL consists of `Type`that describe object types that can be queried on that server and the fields they have.
 - It can return many resources in a single request which makes it faster than REST API.
 
 An example of a type `Project` written using SDL is shown below:
 ```commandline
 type Project {
  name: String!
  id: Int!
}
 ```
The following shows an example of a query using GraphQL which will return all the Project names and ID.


```commandline
Input:
  {
    Project
      name
      id
    }
  }
```


```commandline
Output:
  {
    "data": {
      "Project": {
        "name": "ORCA",
        "id": 1
      }
    }
  }
```

### Pros and cons

Pros:
- Able to get many resources in a single request compared to REST API.
- Able to only fetch the needed information in a single request instead of fetching all the data.
- There is no need to validate the data format, as GraphQL will do the validation. Developers need only to write resolvers – how the data will be received.
- A developer can view the available schemas before making the request.
- There is only one version of GraphQL API thus allowing more maintainable and cleaner code.
- Shows detailed error message including all the resolvers and referring to the exact query part during error in query. This is useful during debugging.
- Centralizes our DB code, making it easier to switch or update DB libraries.

Cons:
- Performance issues with complex queries- it could face performance issues if a client asks for too many nested fields at once.
- Not recommended for small applications. Moreover, the learning curve is higher compared to other methods.
- File uploading is a bit complex.

### GraphQL Servers

There are numerous servers for GraphQL that support different programming languages. A list of all the servers can be seen [here](https://graphql.org/code/).

### Prebuilt GraphQL servers

#### AWS AppSync

- [AWS AppSync](https://aws.amazon.com/appsync/) is a fully managed service that develops GraphQL APIs by handling the heavy lifting of securely connecting to data sources like AWS DynamoDB, Lambda, and more. 
- automatically scales GraphQL API execution engine up and down to meet API request volumes.
- Pricing is $4.00 per million Query and Data Modification Operations and $0.08 per million minutes of connection to the AWS AppSync service. Details of pricing can be found [here](https://aws.amazon.com/appsync/pricing/).
- Details on deploying  AppSync GraphQL API using terraform can be found below.
    - [terraform docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/appsync_graphql_api).
    - [Deploying AppSync with Terraform](https://tech.ovoenergy.com/deploying-appsync-with-terraform/)

:::warning
As of 07/18/2021, AWS AppSync is currently yet not approved in NGAP AWS account by NASA. However, it could be a good future approach when approved. 
:::

#### Hasura

- [Hasura](https://hasura.io/) is an open source service that can create APIs without having to build, operate & scale a GraphQL server.
- Supports GraphQL on Postgres, AWS Aurora, Microsoft SQL server.
- Can be run in [cloud](https://hasura.io/docs/latest/graphql/cloud/getting-started/index.html#cloud-getting-started) (fastest way) or using [docker locally](https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple).
- comes with its own authentication and authorization features. To prevent GraphQL endpoint from being publicly accessible, developers have to create an [admin secret](https://hasura.io/docs/latest/graphql/core/deployment/deployment-guides/docker.html#docker-secure).
- [Pricing](https://hasura.io/pricing/)- Fully managed cloud service is $99/month/project and supports upto 20GB data with $2/additional GB data.
- written in Haskell programming language.

#### PostGraphile 

- [Postgraphile](https://www.graphile.org/postgraphile/) is similar to Hasura and can create GraphQL API from a PostgreSQL schema faster.
- Most operations can be performed using [CLI](https://www.graphile.org/postgraphile/usage-cli/).
- uses PostgreSQL's "role-based grant system" and "row-level security policies".
- [Pricing](https://www.graphile.org/postgraphile/pricing/) is $25/month for PostGraphile Pro which has additional features compared to PostGraphile.

:::tip
 PostGraphile can be deployed using AWS lambda on Mac, Linux or Windows. Check [this example](https://github.com/graphile/postgraphile-lambda-example).
:::

 #### Apollo Server
 - [Apollo Server](https://www.apollographql.com/docs/apollo-server/) is open source and uses javascript.
 - needs [apollo-server](https://npm.im/apollo-server) and [graphql](https://npm.im/graphql) libraries as preriquisites.
 - Pricing- $59/user /month
 - A good example to create the server can be found [here].(https://www.apollographql.com/docs/apollo-server/getting-started/)
 - It can be deployed using lambda in AWS by utilizing serverless framework. A few examples are given below.
   - [How to deploy Apollo Server with AWS Lambda](https://www.apollographql.com/docs/apollo-server/deployment/lambda/)
   - [How to Build a Serverless Apollo GraphQL Server with AWS Lambda, Webpack and TypeScript](https://itnext.io/how-to-build-a-serverless-apollo-graphql-server-with-aws-lambda-webpack-and-typescript-64a377739208)
 - Can be deployed faster using [Heroku](https://www.apollographql.com/docs/apollo-server/deployment/heroku/) but has additional cost.

### Building own GraphQL servers

- [GraphQL.js](https://graphql.org/graphql-js/)- Server using Javascript.
- [Apollo Server](https://www.apollographql.com/docs/)- Server using Javascript.
- [Express GraphQL](https://github.com/graphql/express-graphql)- Server using Javascript.
- [Graphehe](https://github.com/graphql-python/graphene)- Server using Python. Most popular and contributors.
- [Ariadne](https://ariadnegraphql.org/)- Server using Python
- [Strawberry](https://strawberry.rocks/)- Server using Python
- [CMR-GraphQL](https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse)- Currently being used by NASA GHRC developers Check out the example of their GraphQL schema and resolver [here](https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse/cmr-graphql/graphql/graphql.js)


### GraphQL in ORCA

Some of the lambdas that might be affected are:
- post_copy_request_to_queue
- db_deploy
- post_to_database
- request_files
- copy_files_to_archive
- request_status_for_granule
- request_status_for_job
- db_deploy
- post_to_database

:::important
Apart from updating those lambdas, developers need to create the GraphQL endpoint using terraform or AWS SAM, update requirements.txt, requirements-dev.txt or bin/build.sh, bin/run_tests.sh by adding additional dependiencies like `graphene` in case of using graphene, or `npm install apollo-server graphql` in case of using Apollo server.
In case of using Javascript libraries like Apollo server, additional files/codes are needed to write the [schema](https://github.com/serverless/serverless-graphql/blob/master/app-backend/dynamodb/schema.js) and [resolver](https://github.com/serverless/serverless-graphql/blob/master/app-backend/dynamodb/resolvers.js).
In case of using Python library like [Graphene](https://github.com/graphql-python/graphene), developers need to update .py files to import libraries, create class and queries, and to create schema and resolver. 
:::
  
  
  A few suggestions are given below:

#### post_copy_request_to_queue

 - Developers might need to modify `get_metadata_sql(key_path)` and use the graphql query. See this [example](https://docs.graphene-python.org/en/latest/execution/execute/).
 - Update `test_post_copy_request_to_queue.py` based on changes in `post_copy_request_to_queue.py`. One test could be `test_get_metadata_sql_happy_path()`
 - `shared_recovery.update_status_for_file()` and `shared_recovery.post_entry_to_queue()` functions for sending to SQS might need to be removed and  replaced with code that leverages GraphQL to write to the database.
 - Additional changes are expected.

#### copy_files_to_archive

 - `shared_recovery.update_status_for_file()` and `shared_recovery.post_entry_to_queue()` functions for sending to SQS might need to be removed and replaced with code that leverages GraphQL to write to the database.
 - Additional changes are expected.


#### request_files

 - `shared_recovery.update_status_for_file()`, `shared_recovery.create_status_for_job()` and `shared_recovery.post_entry_to_queue()` functions for sending to SQS might need to be removed and replaced with code that leverages GraphQL to write to the database.
 - `db_queue_url` arg in `inner_task()` will not be needed if SQS is not used.
 - Modify `process_granule()` function.
 - Additional changes are expected.

#### request_status_for_granule

 - Modify `get_most_recent_job_id_for_granule()` function to use GraphQL query.
 - Modify `get_status_totals_for_job()` function to use GraphQL query.
 - Additional changes are expected.

#### request_status_for_job

- Modify `get_granule_status_entries_for_job()` function to use GraphQL query.
- Modify `get_granule_status_entries_for_job()` function to use GraphQL query.

#### db_deploy

- `app_db_exists()`, `app_schema_exists()`, `app_version_table_exists()` and `get_migration_version()` functions might need to be updated.
- Additional changes are expected.

#### post_to_database

- This will need to be removed if GraphQL is used since it will write to the DB instead of SQS.

### GraphQL server recommendation

Based on this research, GraphQL has a higher learning curve compared to other technologies and will take some time for developers to learn and then implement. If using Javascript libraries, developers should have good background in this language in order to execute this approach. Using some prebuilt GraphQL servers that automatically generates GraphQL schema and resolvers could save some time and simplify the design. Building a prototype in ORCA could reveal if it is worth the effort and time. However, using lambda, API gateway and SQS(the resources in existing ORCA architecture) seem to contain more resources and examples online than GraphQL.

#### Recommendation #1- [Hasura](https://hasura.io/)

- Hasura GraphQL engine can be deployed using Docker and Docker Compose or using Hasura cloud. 
- The easiest way to set up Hasura GraphQL engine on local environment without any cost is using Docker. 
- It supports GraphQL on Postgres, AWS Aurora and seems to be compatible with the current ORCA architecture. 
- Cost to use the cloud is $99/month/project and supports up to 20GB data with $2/additional GB data. 
- Creating the server using the given [`docker-compose.yml`](https://github.com/hasura/graphql-engine/blob/stable/install-manifests/docker-compose/docker-compose.yaml) file will be easy and the server can be queried from the Hasura console. Instructions to create the server can be found [here](https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple).
- Instructions on connecting Postgres to the GraphQL server can be found [here](https://hasura.io/docs/latest/graphql/cloud/getting-started/cloud-databases/aws-postgres.html#cloud-db-aws-rds-postgres)
:::warning
Hasura cloud service is not approved by NGAP, so it cannot be used for now. However, developers can use the docker version for testing.
:::

##### Practical Evaluation
- Setting up locally is the easiest out of all three recommendations.
- Only supports PostgreSQL, MS SQL Server, and Citrus, with BigQuery in beta.
- Did not attempt to deploy to AWS.


#### Recommendation #2- [Apollo Server](https://www.apollographql.com/)

- This server has to be built from scratch and developer has to be familiar with Javascript. 
- It is completely free and has over 108,000 users and 400+ contributors which make it a good candidate to look into further for prototyping.
- Developer has to write his  own GraphQL schema when using this method which could be time consuming.
- Developers have to work with two libraries that are required by the server:
    - [apollo-server](https://npm.im/apollo-server): library for Apollo Server which defines the shape of the data and how to fetch it.
    - [graphql](https://www.npmjs.com/package/graphql): library used to build a GraphQL schema and execute queries against it.
- Some examples of the schema and resolvers for this server can be found [here](https://www.apollographql.com/docs/apollo-server/getting-started/).
- Once created, GraphQL queries can be executed from Apollo Sandbox console.

##### Practical Evaluation
- Documentation is severely limited, with the section for connecting to databases [requesting additional coders to complete missing functionality](https://www.apollographql.com/docs/tutorial/data-source/).
- Some tutorials exist, but they are [generally a few years old and out-of-date](https://www.robinwieruch.de/graphql-apollo-server-tutorial).
- Recommendations use auto-magical Sequelize integration, which may not give us a solid boundary should DB technology change.
  - Unsure if the driver would correctly handle [Aurora Serverless](research-AuroraServerless.md) errors.
- Deployment is similarly undocumented. The [best source](https://levelup.gitconnected.com/deploying-an-apollo-graphql-application-as-an-aws-lambda-function-through-serverless-77fa33612bae) states outright that deployment is over-complicated, so developers should rely on "serverless" which we cannot use in our current architecture.
- Attempted to create resources manually, invoked, and got
  ```
  {
    "errorType": "Error",
    "errorMessage": "Unable to determine event source based on event.",
    "trace": [
      "Error: Unable to determine event source based on event.",
      "    at getEventSourceNameBasedOnEvent (/var/task/node_modules/@vendia/serverless-express/src/event-sources/utils.js:79:9)",
      "    at proxy (/var/task/node_modules/@vendia/serverless-express/src/configure.js:37:51)",
      "    at handler (/var/task/node_modules/@vendia/serverless-express/src/configure.js:95:12)",
      "    at Runtime.handler (/var/task/node_modules/apollo-server-lambda/dist/ApolloServer.js:51:27)"
    ]
  }
  ```


#### Recommendation #3- [Graphene](https://github.com/graphql-python/graphene)

- Python library with 9000+ users for building GraphQL schemas/types. Since all ORCA lambdas are written in Python, using this library will make it easier for code changes.
- Instead of writing GraphQL Schema Definition Language, developers will use Python code to describe the data provided by the server.
- Can be deployed using lambda function with the help of [SAM]https://github.com/ivanchoo/demo-aws-graphql-python/blob/master/template.yml) or cloudformation. So serverless approach will charge when it is only used.

##### Practical Evaluation
- More flexible than other libraries; Would be much easier to switch DB technology.
  - Could use current database code.
- Deployed something using [these basic instructions](https://thomasstep.com/blog/graphene-and-lambda-functions)
  - Can't access any form of UI.
  - Looking at code, UI/UI-Endpoints may not be present. Requires `query` in Lambda input.
  - Without UI, doesn't have any advantage over building our own MS.
  - Filtering functions.
    ```json
    {
      "query": "query doesnotmatter{ mirror(word: \"apples\") { backward } }"
    }
    ```
    ```json
    {
      "statusCode": 200,
      "body": "{\"mirror\": {\"backward\": \"selppa\"}}"
    }
    ```
  - Errors are not properly communicated, instead returning 200 with a "null" body.
    - Could be fixed with further development.


### GraphQL IDE
There are a few IDE that developers can use to interact with GraphQL API calls and query the server.
- [GraphiQL](https://github.com/graphql/graphiql). The live IDE can be seen [here](http://graphql.org/swapi-graphql). 
- [GraphQL Playground](https://github.com/graphql/graphql-playground)
- [GraphQL IDE](https://github.com/andev-software/graphql-ide)

### Useful tools
The following tools might be useful for developers while working with GraphQL
- GraphQL CLI- CLI for GraphQL development workflows.
- GraphQL Docs- generates GraphQL documents. 
- GraphDoc- generates GraphQL documents.
- GraphQL Network- useful for debugging.
- GraphQL Voyager- for visualizing data relations.
- GraphQL Config- useful for configuring dev environment with GraphQL schema.
- GraphQL Bindings- SDK for sharing GraphQL APIs
- GraphQL Boilerplates- useful for backend projects.
- Apollo Graph Manager-  useful for monitoring the performance and usage of GraphQL backend.

### Recommendation
While GraphQL is an interesting technology, the lack of documentation makes implementation difficult.
In particular, deployment and integration lack vital instructions, with most tutorials running in a docker container or a Python script rather than a realistic environment.
At this time, I recommend not radically adjusting our architecture to work in a poorly documented and developed library, especially as we are likely to discover further pain-points.
Even the one example that was functional in AWS had major flaws, such as a lack of proper error reporting, though this could be fixed with further development.
Simply put, There would need to be significant research and development before our GraphQL functionality would reach our current level of database integration.

### Future Options
Should this be desired, I feel strongly that Graphene is the only known option that gives us the flexibility that is required to justify this level of adaptation.
Research would be required for:
- Ideal deployment method
- Accessing API + Error Codes
- Security
- GraphQL UI for use in development

Alternatively, GraphQL could theoretically be run in an EC2 instance managed by an orchestration service such as [Fargate](https://aws.amazon.com/fargate/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc&fargate-blogs.sort-by=item.additionalFields.createdDate&fargate-blogs.sort-order=desc) with some form of connecting layer providing an API, but this is untested and would need research and cost analysis.

##### References
- https://graphql.org/learn/queries/
- https://github.com/graphql-python
- https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/
- https://hasura.io/docs/latest/graphql/core/index.html
- https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple
- https://www.moesif.com/blog/graphql/technical/Ways-To-Add-GraphQL-To-Your-Postgres-Database-Comparing-Hasura-Prisma-and-Others/
- https://docs.graphene-python.org/en/latest/quickstart/
- https://github.com/ivanchoo/demo-aws-graphql-python
- https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse