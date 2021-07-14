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


## Deploying GraphQL Server

..................







## GraphQL in ORCA

Some of the lambdas that will be affected are:
- post_copy_request_to_queue
- db_deploy
- post_to_database
- request_files
- copy_files_to_archive
- request_status_for_granule
- request_status_for_granule

:::tip
Currently, there is an IDE named [GraphiQL](https://github.com/graphql/graphiql)that can interact with GraphQL API calls and developers can query the server. 
The live IDE can be seen [here](http://graphql.org/swapi-graphql). 
:::

#### Sources
- https://graphql.org/learn/queries/
- https://github.com/graphql-python
- https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/
