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

## Pros and cons

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


## GraphQL Server

There are numerous servers for GraphQL that support different programming languages. A list of all the servers can be seen [here](https://graphql.org/code/).
:::tip
Popular servers using Javascript include [GraphQL.js](https://graphql.org/graphql-js/), [Apollo Server](https://www.apollographql.com/docs/) and [Express GraphQL](https://github.com/graphql/express-graphql).
Popular servers using Python include [Graphehe](https://github.com/graphql-python/graphene), [Ariadne](https://ariadnegraphql.org/) and [Strawberry](https://strawberry.rocks/).
:::


## AWS AppSync

AWS AppSync is a fully managed service that develops GraphQL APIs by handling the heavy lifting of securely connecting to data sources like AWS DynamoDB, Lambda, and more. AWS AppSync automatically scales GraphQL API execution engine up and down to meet API request volumes. 
:::tip
Details on creating and configuring a GraphQL API using AppSync can be found [here](https://docs.aws.amazon.com/appsync/latest/devguide/quickstart-launch-a-sample-schema.html).
:::



## GraphQL in ORCA

Some of the lambdas that will be affected are:
- post_copy_request_to_queue
- db_deploy
- post_to_database
- request_files
- copy_files_to_archive
- request_status_for_granule
- request_status_for_granule

## GraphQL IDE
There are a few IDE that developers can use to interact with GraphQL API calls and query the server.
- [GraphiQL](https://github.com/graphql/graphiql). The live IDE can be seen [here](http://graphql.org/swapi-graphql). 
- [GraphQL Playground](https://github.com/graphql/graphql-playground)
- [GraphQL IDE](https://github.com/andev-software/graphql-ide)

## Useful tools
The following tools might be  uueful for developers while working with GraphQL
- GraphQL CLI- CLI for GraphQL development workflows.
- GraphQL Docs- generates GraphQL documents.
- GraphDoc- generates GraphQL documents.
- GraphQL Network- useful for debugging.
- GraphQL Voyager- for visualizing data relations.
- GraphQL Config- useful for configuring dev environment with GraphQL schema.
- GraphQL Bindings- SDK for sharing GraphQL APIs
- GraphQL Boilerplates- useful for backend projects.

#### Sources
- https://graphql.org/learn/queries/
- https://github.com/graphql-python
- https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/
