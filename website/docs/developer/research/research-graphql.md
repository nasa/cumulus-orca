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
 - It can return many resources in a single request which makes it faster then REST API.
 
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
- A developer can view the available data before making the request.
- There is only one version of GraphQL API thus allowing more maintainable and cleaner code.
- Shows detailed error message including all the resolvers and referring to the exact query part during error in query. This is useful during debugging.

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

:::tip
Details on creating and configuring a GraphQL API using AppSync can be found [here](https://docs.aws.amazon.com/appsync/latest/devguide/quickstart-launch-a-sample-schema.html).
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


### GraphQL in ORCA

Some of the lambdas that will be affected are:
- post_copy_request_to_queue
- db_deploy
- post_to_database
- request_files
- copy_files_to_archive
- request_status_for_granule
- request_status_for_granule

### GraphQL IDE
There are a few IDE that developers can use to interact with GraphQL API calls and query the server.
- [GraphiQL](https://github.com/graphql/graphiql). The live IDE can be seen [here](http://graphql.org/swapi-graphql). 
- [GraphQL Playground](https://github.com/graphql/graphql-playground)
- [GraphQL IDE](https://github.com/andev-software/graphql-ide)

### Useful tools
The following tools might be  uueful for developers while working with GraphQL
- GraphQL CLI- CLI for GraphQL development workflows.
- GraphQL Docs- generates GraphQL documents.
- GraphDoc- generates GraphQL documents.
- GraphQL Network- useful for debugging.
- GraphQL Voyager- for visualizing data relations.
- GraphQL Config- useful for configuring dev environment with GraphQL schema.
- GraphQL Bindings- SDK for sharing GraphQL APIs
- GraphQL Boilerplates- useful for backend projects.
- Apollo Graph Manager-  useful for monitoring the performance and usage of GraphQL backend.

##### Sources
- https://graphql.org/learn/queries/
- https://github.com/graphql-python
- https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/
- https://hasura.io/docs/latest/graphql/core/index.html
- https://www.moesif.com/blog/graphql/technical/Ways-To-Add-GraphQL-To-Your-Postgres-Database-Comparing-Hasura-Prisma-and-Others/
