"use strict";(self.webpackChunkorca_website=self.webpackChunkorca_website||[]).push([[6326],{3905:(e,t,a)=>{a.d(t,{Zo:()=>u,kt:()=>m});var r=a(7294);function n(e,t,a){return t in e?Object.defineProperty(e,t,{value:a,enumerable:!0,configurable:!0,writable:!0}):e[t]=a,e}function l(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,r)}return a}function o(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?l(Object(a),!0).forEach((function(t){n(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):l(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}function i(e,t){if(null==e)return{};var a,r,n=function(e,t){if(null==e)return{};var a,r,n={},l=Object.keys(e);for(r=0;r<l.length;r++)a=l[r],t.indexOf(a)>=0||(n[a]=e[a]);return n}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(r=0;r<l.length;r++)a=l[r],t.indexOf(a)>=0||Object.prototype.propertyIsEnumerable.call(e,a)&&(n[a]=e[a])}return n}var s=r.createContext({}),p=function(e){var t=r.useContext(s),a=t;return e&&(a="function"==typeof e?e(t):o(o({},t),e)),a},u=function(e){var t=p(e.components);return r.createElement(s.Provider,{value:t},e.children)},h="mdxType",d={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},c=r.forwardRef((function(e,t){var a=e.components,n=e.mdxType,l=e.originalType,s=e.parentName,u=i(e,["components","mdxType","originalType","parentName"]),h=p(a),c=n,m=h["".concat(s,".").concat(c)]||h[c]||d[c]||l;return a?r.createElement(m,o(o({ref:t},u),{},{components:a})):r.createElement(m,o({ref:t},u))}));function m(e,t){var a=arguments,n=t&&t.mdxType;if("string"==typeof e||n){var l=a.length,o=new Array(l);o[0]=c;var i={};for(var s in t)hasOwnProperty.call(t,s)&&(i[s]=t[s]);i.originalType=e,i[h]="string"==typeof e?e:n,o[1]=i;for(var p=2;p<l;p++)o[p]=a[p];return r.createElement.apply(null,o)}return r.createElement.apply(null,a)}c.displayName="MDXCreateElement"},4709:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>s,contentTitle:()=>o,default:()=>d,frontMatter:()=>l,metadata:()=>i,toc:()=>p});var r=a(7462),n=(a(7294),a(3905));const l={id:"research-graphql",title:"GraphQL Research Notes",description:"Research Notes on GraphQL."},o=void 0,i={unversionedId:"developer/research/research-graphql",id:"developer/research/research-graphql",title:"GraphQL Research Notes",description:"Research Notes on GraphQL.",source:"@site/docs/developer/research/research-graphql.md",sourceDirName:"developer/research",slug:"/developer/research/research-graphql",permalink:"/cumulus-orca/docs/developer/research/research-graphql",draft:!1,editUrl:"https://github.com/nasa/cumulus-orca/edit/develop/website/docs/developer/research/research-graphql.md",tags:[],version:"current",frontMatter:{id:"research-graphql",title:"GraphQL Research Notes",description:"Research Notes on GraphQL."},sidebar:"dev_guide",previous:{title:"Aurora Serverless Research Notes",permalink:"/cumulus-orca/docs/developer/research/research-AuroraServerless"},next:{title:"Multipart Chunksize Research Notes",permalink:"/cumulus-orca/docs/developer/research/research-multipart-chunksize"}},s={},p=[{value:"Overview",id:"overview",level:2},{value:"Pros and cons",id:"pros-and-cons",level:3},{value:"GraphQL Servers",id:"graphql-servers",level:3},{value:"Prebuilt GraphQL servers",id:"prebuilt-graphql-servers",level:3},{value:"AWS AppSync",id:"aws-appsync",level:4},{value:"Hasura",id:"hasura",level:4},{value:"PostGraphile",id:"postgraphile",level:4},{value:"Apollo Server",id:"apollo-server",level:4},{value:"Building own GraphQL servers",id:"building-own-graphql-servers",level:3},{value:"GraphQL in ORCA",id:"graphql-in-orca",level:3},{value:"post_copy_request_to_queue",id:"post_copy_request_to_queue",level:4},{value:"copy_from_archive",id:"copy_from_archive",level:4},{value:"request_from_archive",id:"request_from_archive",level:4},{value:"request_status_for_granule",id:"request_status_for_granule",level:4},{value:"request_status_for_job",id:"request_status_for_job",level:4},{value:"db_deploy",id:"db_deploy",level:4},{value:"post_to_database",id:"post_to_database",level:4},{value:"GraphQL server recommendation",id:"graphql-server-recommendation",level:3},{value:"Recommendation #1- Hasura",id:"recommendation-1--hasura",level:4},{value:"Practical Evaluation",id:"practical-evaluation",level:5},{value:"Recommendation #2- Apollo Server",id:"recommendation-2--apollo-server",level:4},{value:"Practical Evaluation",id:"practical-evaluation-1",level:5},{value:"Recommendation #3- Graphene",id:"recommendation-3--graphene",level:4},{value:"Practical Evaluation",id:"practical-evaluation-2",level:5},{value:"GraphQL IDE",id:"graphql-ide",level:3},{value:"Useful tools",id:"useful-tools",level:3},{value:"Recommendation",id:"recommendation",level:3},{value:"Future Options",id:"future-options",level:3},{value:"References",id:"references",level:5}],u={toc:p},h="wrapper";function d(e){let{components:t,...a}=e;return(0,n.kt)(h,(0,r.Z)({},u,a,{components:t,mdxType:"MDXLayout"}),(0,n.kt)("h2",{id:"overview"},"Overview"),(0,n.kt)("p",null,(0,n.kt)("a",{parentName:"p",href:"https://graphql.org/"},"GraphQL")," is an open-source data query and manipulation language for APIs, and a runtime for fulfilling queries with existing data."),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"A GraphQL server provides a client with a predefined schema written down in Schema Definition Language (SDL). "),(0,n.kt)("li",{parentName:"ul"},"The schema defines the queries that can be made."),(0,n.kt)("li",{parentName:"ul"},"The SDL consists of ",(0,n.kt)("inlineCode",{parentName:"li"},"Type"),"that describe object types that can be queried on that server and the fields they have."),(0,n.kt)("li",{parentName:"ul"},"It can return many resources in a single request which makes it faster than REST API."," An example of a type ",(0,n.kt)("inlineCode",{parentName:"li"},"Project")," written using SDL is shown below:",(0,n.kt)("pre",{parentName:"li"},(0,n.kt)("code",{parentName:"pre",className:"language-commandline"},"type Project {\n name: String!\n id: Int!\n}\n")),"The following shows an example of a query using GraphQL which will return all the Project names and ID.")),(0,n.kt)("pre",null,(0,n.kt)("code",{parentName:"pre",className:"language-commandline"},"Input:\n  {\n    Project\n      name\n      id\n    }\n  }\n")),(0,n.kt)("pre",null,(0,n.kt)("code",{parentName:"pre",className:"language-commandline"},'Output:\n  {\n    "data": {\n      "Project": {\n        "name": "ORCA",\n        "id": 1\n      }\n    }\n  }\n')),(0,n.kt)("h3",{id:"pros-and-cons"},"Pros and cons"),(0,n.kt)("p",null,"Pros:"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Able to get many resources in a single request compared to REST API."),(0,n.kt)("li",{parentName:"ul"},"Able to only fetch the needed information in a single request instead of fetching all the data."),(0,n.kt)("li",{parentName:"ul"},"There is no need to validate the data format, as GraphQL will do the validation. Developers need only to write resolvers \u2013 how the data will be received."),(0,n.kt)("li",{parentName:"ul"},"A developer can view the available schemas before making the request."),(0,n.kt)("li",{parentName:"ul"},"There is only one version of GraphQL API thus allowing more maintainable and cleaner code."),(0,n.kt)("li",{parentName:"ul"},"Shows detailed error message including all the resolvers and referring to the exact query part during error in query. This is useful during debugging."),(0,n.kt)("li",{parentName:"ul"},"Centralizes our DB code, making it easier to switch or update DB libraries.")),(0,n.kt)("p",null,"Cons:"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Performance issues with complex queries- it could face performance issues if a client asks for too many nested fields at once."),(0,n.kt)("li",{parentName:"ul"},"Not recommended for small applications. Moreover, the learning curve is higher compared to other methods."),(0,n.kt)("li",{parentName:"ul"},"File uploading is a bit complex.")),(0,n.kt)("h3",{id:"graphql-servers"},"GraphQL Servers"),(0,n.kt)("p",null,"There are numerous servers for GraphQL that support different programming languages. A list of all the servers can be seen ",(0,n.kt)("a",{parentName:"p",href:"https://graphql.org/code/"},"here"),"."),(0,n.kt)("h3",{id:"prebuilt-graphql-servers"},"Prebuilt GraphQL servers"),(0,n.kt)("h4",{id:"aws-appsync"},"AWS AppSync"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://aws.amazon.com/appsync/"},"AWS AppSync")," is a fully managed service that develops GraphQL APIs by handling the heavy lifting of securely connecting to data sources like AWS DynamoDB, Lambda, and more. "),(0,n.kt)("li",{parentName:"ul"},"automatically scales GraphQL API execution engine up and down to meet API request volumes."),(0,n.kt)("li",{parentName:"ul"},"Pricing is $4.00 per million Query and Data Modification Operations and $0.08 per million minutes of connection to the AWS AppSync service. Details of pricing can be found ",(0,n.kt)("a",{parentName:"li",href:"https://aws.amazon.com/appsync/pricing/"},"here"),"."),(0,n.kt)("li",{parentName:"ul"},"Details on deploying  AppSync GraphQL API using terraform can be found below.",(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/appsync_graphql_api"},"terraform docs"),"."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://tech.ovoenergy.com/deploying-appsync-with-terraform/"},"Deploying AppSync with Terraform"))))),(0,n.kt)("admonition",{type:"warning"},(0,n.kt)("p",{parentName:"admonition"},"As of 07/18/2021, AWS AppSync is currently yet not approved in NGAP AWS account by NASA. However, it could be a good future approach when approved. ")),(0,n.kt)("h4",{id:"hasura"},"Hasura"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/"},"Hasura")," is an open source service that can create APIs without having to build, operate & scale a GraphQL server."),(0,n.kt)("li",{parentName:"ul"},"Supports GraphQL on Postgres, AWS Aurora, Microsoft SQL server."),(0,n.kt)("li",{parentName:"ul"},"Can be run in ",(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/cloud/getting-started/index.html#cloud-getting-started"},"cloud")," (fastest way) or using ",(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple"},"docker locally"),"."),(0,n.kt)("li",{parentName:"ul"},"comes with its own authentication and authorization features. To prevent GraphQL endpoint from being publicly accessible, developers have to create an ",(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/core/deployment/deployment-guides/docker.html#docker-secure"},"admin secret"),"."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/pricing/"},"Pricing"),"- Fully managed cloud service is $99/month/project and supports upto 20GB data with $2/additional GB data."),(0,n.kt)("li",{parentName:"ul"},"written in Haskell programming language.")),(0,n.kt)("h4",{id:"postgraphile"},"PostGraphile"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.graphile.org/postgraphile/"},"Postgraphile")," is similar to Hasura and can create GraphQL API from a PostgreSQL schema faster."),(0,n.kt)("li",{parentName:"ul"},"Most operations can be performed using ",(0,n.kt)("a",{parentName:"li",href:"https://www.graphile.org/postgraphile/usage-cli/"},"CLI"),"."),(0,n.kt)("li",{parentName:"ul"},'uses PostgreSQL\'s "role-based grant system" and "row-level security policies".'),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.graphile.org/postgraphile/pricing/"},"Pricing")," is $25/month for PostGraphile Pro which has additional features compared to PostGraphile.")),(0,n.kt)("admonition",{type:"tip"},(0,n.kt)("p",{parentName:"admonition"}," PostGraphile can be deployed using AWS lambda on Mac, Linux or Windows. Check ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/graphile/postgraphile-lambda-example"},"this example"),".")),(0,n.kt)("h4",{id:"apollo-server"},"Apollo Server"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/apollo-server/"},"Apollo Server")," is open source and uses javascript."),(0,n.kt)("li",{parentName:"ul"},"needs ",(0,n.kt)("a",{parentName:"li",href:"https://npm.im/apollo-server"},"apollo-server")," and ",(0,n.kt)("a",{parentName:"li",href:"https://npm.im/graphql"},"graphql")," libraries as preriquisites."),(0,n.kt)("li",{parentName:"ul"},"Pricing- $59/user /month"),(0,n.kt)("li",{parentName:"ul"},"A good example to create the server can be found ","[here]",".(",(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/apollo-server/getting-started/"},"https://www.apollographql.com/docs/apollo-server/getting-started/"),")"),(0,n.kt)("li",{parentName:"ul"},"It can be deployed using lambda in AWS by utilizing serverless framework. A few examples are given below.",(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/apollo-server/deployment/lambda/"},"How to deploy Apollo Server with AWS Lambda")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://itnext.io/how-to-build-a-serverless-apollo-graphql-server-with-aws-lambda-webpack-and-typescript-64a377739208"},"How to Build a Serverless Apollo GraphQL Server with AWS Lambda, Webpack and TypeScript")))),(0,n.kt)("li",{parentName:"ul"},"Can be deployed faster using ",(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/apollo-server/deployment/heroku/"},"Heroku")," but has additional cost.")),(0,n.kt)("h3",{id:"building-own-graphql-servers"},"Building own GraphQL servers"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://graphql.org/graphql-js/"},"GraphQL.js"),"- Server using Javascript."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/"},"Apollo Server"),"- Server using Javascript."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/graphql/express-graphql"},"Express GraphQL"),"- Server using Javascript."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/graphql-python/graphene"},"Graphehe"),"- Server using Python. Most popular and contributors."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://ariadnegraphql.org/"},"Ariadne"),"- Server using Python"),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://strawberry.rocks/"},"Strawberry"),"- Server using Python"),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse"},"CMR-GraphQL"),"- Currently being used by NASA GHRC developers Check out the example of their GraphQL schema and resolver ",(0,n.kt)("a",{parentName:"li",href:"https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse/cmr-graphql/graphql/graphql.js"},"here"))),(0,n.kt)("h3",{id:"graphql-in-orca"},"GraphQL in ORCA"),(0,n.kt)("p",null,"Some of the lambdas that might be affected are:"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"post_copy_request_to_queue"),(0,n.kt)("li",{parentName:"ul"},"db_deploy"),(0,n.kt)("li",{parentName:"ul"},"post_to_database"),(0,n.kt)("li",{parentName:"ul"},"request_from_archive"),(0,n.kt)("li",{parentName:"ul"},"copy_from_archive"),(0,n.kt)("li",{parentName:"ul"},"request_status_for_granule"),(0,n.kt)("li",{parentName:"ul"},"request_status_for_job"),(0,n.kt)("li",{parentName:"ul"},"db_deploy"),(0,n.kt)("li",{parentName:"ul"},"post_to_database")),(0,n.kt)("admonition",{type:"important"},(0,n.kt)("p",{parentName:"admonition"},"Apart from updating those lambdas, developers need to create the GraphQL endpoint using terraform or AWS SAM, update requirements.txt, requirements-dev.txt or bin/build.sh, bin/run_tests.sh by adding additional dependiencies like ",(0,n.kt)("inlineCode",{parentName:"p"},"graphene")," in case of using graphene, or ",(0,n.kt)("inlineCode",{parentName:"p"},"npm install apollo-server graphql")," in case of using Apollo server.\nIn case of using Javascript libraries like Apollo server, additional files/codes are needed to write the ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/serverless/serverless-graphql/blob/master/app-backend/dynamodb/schema.js"},"schema")," and ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/serverless/serverless-graphql/blob/master/app-backend/dynamodb/resolvers.js"},"resolver"),".\nIn case of using Python library like ",(0,n.kt)("a",{parentName:"p",href:"https://github.com/graphql-python/graphene"},"Graphene"),", developers need to update .py files to import libraries, create class and queries, and to create schema and resolver. ")),(0,n.kt)("p",null,"  A few suggestions are given below:"),(0,n.kt)("h4",{id:"post_copy_request_to_queue"},"post_copy_request_to_queue"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Developers might need to modify ",(0,n.kt)("inlineCode",{parentName:"li"},"get_metadata_sql(key_path)")," and use the graphql query. See this ",(0,n.kt)("a",{parentName:"li",href:"https://docs.graphene-python.org/en/latest/execution/execute/"},"example"),"."),(0,n.kt)("li",{parentName:"ul"},"Update ",(0,n.kt)("inlineCode",{parentName:"li"},"test_post_copy_request_to_queue.py")," based on changes in ",(0,n.kt)("inlineCode",{parentName:"li"},"post_copy_request_to_queue.py"),". One test could be ",(0,n.kt)("inlineCode",{parentName:"li"},"test_get_metadata_sql_happy_path()")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.update_status_for_file()")," and ",(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.post_entry_to_queue()")," functions for sending to SQS might need to be removed and  replaced with code that leverages GraphQL to write to the database."),(0,n.kt)("li",{parentName:"ul"},"Additional changes are expected.")),(0,n.kt)("h4",{id:"copy_from_archive"},"copy_from_archive"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.update_status_for_file()")," and ",(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.post_entry_to_queue()")," functions for sending to SQS might need to be removed and replaced with code that leverages GraphQL to write to the database."),(0,n.kt)("li",{parentName:"ul"},"Additional changes are expected.")),(0,n.kt)("h4",{id:"request_from_archive"},"request_from_archive"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.update_status_for_file()"),", ",(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.create_status_for_job()")," and ",(0,n.kt)("inlineCode",{parentName:"li"},"shared_recovery.post_entry_to_queue()")," functions for sending to SQS might need to be removed and replaced with code that leverages GraphQL to write to the database."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("inlineCode",{parentName:"li"},"db_queue_url")," arg in ",(0,n.kt)("inlineCode",{parentName:"li"},"inner_task()")," will not be needed if SQS is not used."),(0,n.kt)("li",{parentName:"ul"},"Modify ",(0,n.kt)("inlineCode",{parentName:"li"},"process_granule()")," function."),(0,n.kt)("li",{parentName:"ul"},"Additional changes are expected.")),(0,n.kt)("h4",{id:"request_status_for_granule"},"request_status_for_granule"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Modify ",(0,n.kt)("inlineCode",{parentName:"li"},"get_most_recent_job_id_for_granule()")," function to use GraphQL query."),(0,n.kt)("li",{parentName:"ul"},"Modify ",(0,n.kt)("inlineCode",{parentName:"li"},"get_status_totals_for_job()")," function to use GraphQL query."),(0,n.kt)("li",{parentName:"ul"},"Additional changes are expected.")),(0,n.kt)("h4",{id:"request_status_for_job"},"request_status_for_job"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Modify ",(0,n.kt)("inlineCode",{parentName:"li"},"get_granule_status_entries_for_job()")," function to use GraphQL query."),(0,n.kt)("li",{parentName:"ul"},"Modify ",(0,n.kt)("inlineCode",{parentName:"li"},"get_granule_status_entries_for_job()")," function to use GraphQL query.")),(0,n.kt)("h4",{id:"db_deploy"},"db_deploy"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("inlineCode",{parentName:"li"},"app_db_exists()"),", ",(0,n.kt)("inlineCode",{parentName:"li"},"app_schema_exists()"),", ",(0,n.kt)("inlineCode",{parentName:"li"},"app_version_table_exists()")," and ",(0,n.kt)("inlineCode",{parentName:"li"},"get_migration_version()")," functions might need to be updated."),(0,n.kt)("li",{parentName:"ul"},"Additional changes are expected.")),(0,n.kt)("h4",{id:"post_to_database"},"post_to_database"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"This will need to be removed if GraphQL is used since it will write to the DB instead of SQS.")),(0,n.kt)("h3",{id:"graphql-server-recommendation"},"GraphQL server recommendation"),(0,n.kt)("p",null,"Based on this research, GraphQL has a higher learning curve compared to other technologies and will take some time for developers to learn and then implement. If using Javascript libraries, developers should have good background in this language in order to execute this approach. Using some prebuilt GraphQL servers that automatically generates GraphQL schema and resolvers could save some time and simplify the design. Building a prototype in ORCA could reveal if it is worth the effort and time. However, using lambda, API gateway and SQS(the resources in existing ORCA architecture) seem to contain more resources and examples online than GraphQL."),(0,n.kt)("h4",{id:"recommendation-1--hasura"},"Recommendation #1- ",(0,n.kt)("a",{parentName:"h4",href:"https://hasura.io/"},"Hasura")),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Hasura GraphQL engine can be deployed using Docker and Docker Compose or using Hasura cloud. "),(0,n.kt)("li",{parentName:"ul"},"The easiest way to set up Hasura GraphQL engine on local environment without any cost is using Docker. "),(0,n.kt)("li",{parentName:"ul"},"It supports GraphQL on Postgres, AWS Aurora and seems to be compatible with the current ORCA architecture. "),(0,n.kt)("li",{parentName:"ul"},"Cost to use the cloud is $99/month/project and supports up to 20GB data with $2/additional GB data. "),(0,n.kt)("li",{parentName:"ul"},"Creating the server using the given ",(0,n.kt)("a",{parentName:"li",href:"https://github.com/hasura/graphql-engine/blob/stable/install-manifests/docker-compose/docker-compose.yaml"},(0,n.kt)("inlineCode",{parentName:"a"},"docker-compose.yml"))," file will be easy and the server can be queried from the Hasura console. Instructions to create the server can be found ",(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple"},"here"),"."),(0,n.kt)("li",{parentName:"ul"},"Instructions on connecting Postgres to the GraphQL server can be found ",(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/cloud/getting-started/cloud-databases/aws-postgres.html#cloud-db-aws-rds-postgres"},"here"),(0,n.kt)("admonition",{parentName:"li",type:"warning"},(0,n.kt)("p",{parentName:"admonition"},"Hasura cloud service is not approved by NGAP, so it cannot be used for now. However, developers can use the docker version for testing.")))),(0,n.kt)("h5",{id:"practical-evaluation"},"Practical Evaluation"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Setting up locally is the easiest out of all three recommendations."),(0,n.kt)("li",{parentName:"ul"},"Only supports PostgreSQL, MS SQL Server, and Citrus, with BigQuery in beta."),(0,n.kt)("li",{parentName:"ul"},"Did not attempt to deploy to AWS.")),(0,n.kt)("h4",{id:"recommendation-2--apollo-server"},"Recommendation #2- ",(0,n.kt)("a",{parentName:"h4",href:"https://www.apollographql.com/"},"Apollo Server")),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"This server has to be built from scratch and developer has to be familiar with Javascript. "),(0,n.kt)("li",{parentName:"ul"},"It is completely free and has over 108,000 users and 400+ contributors which make it a good candidate to look into further for prototyping."),(0,n.kt)("li",{parentName:"ul"},"Developer has to write his  own GraphQL schema when using this method which could be time consuming."),(0,n.kt)("li",{parentName:"ul"},"Developers have to work with two libraries that are required by the server:",(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://npm.im/apollo-server"},"apollo-server"),": library for Apollo Server which defines the shape of the data and how to fetch it."),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.npmjs.com/package/graphql"},"graphql"),": library used to build a GraphQL schema and execute queries against it."))),(0,n.kt)("li",{parentName:"ul"},"Some examples of the schema and resolvers for this server can be found ",(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/apollo-server/getting-started/"},"here"),"."),(0,n.kt)("li",{parentName:"ul"},"Once created, GraphQL queries can be executed from Apollo Sandbox console.")),(0,n.kt)("h5",{id:"practical-evaluation-1"},"Practical Evaluation"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Documentation is severely limited, with the section for connecting to databases ",(0,n.kt)("a",{parentName:"li",href:"https://www.apollographql.com/docs/tutorial/data-source/"},"requesting additional coders to complete missing functionality"),"."),(0,n.kt)("li",{parentName:"ul"},"Some tutorials exist, but they are ",(0,n.kt)("a",{parentName:"li",href:"https://www.robinwieruch.de/graphql-apollo-server-tutorial"},"generally a few years old and out-of-date"),"."),(0,n.kt)("li",{parentName:"ul"},"Recommendations use auto-magical Sequelize integration, which may not give us a solid boundary should DB technology change.",(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},"Unsure if the driver would correctly handle ",(0,n.kt)("a",{parentName:"li",href:"/cumulus-orca/docs/developer/research/research-AuroraServerless"},"Aurora Serverless")," errors."))),(0,n.kt)("li",{parentName:"ul"},"Deployment is similarly undocumented. The ",(0,n.kt)("a",{parentName:"li",href:"https://levelup.gitconnected.com/deploying-an-apollo-graphql-application-as-an-aws-lambda-function-through-serverless-77fa33612bae"},"best source"),' states outright that deployment is over-complicated, so developers should rely on "serverless" which we cannot use in our current architecture.'),(0,n.kt)("li",{parentName:"ul"},"Attempted to create resources manually, invoked, and got",(0,n.kt)("pre",{parentName:"li"},(0,n.kt)("code",{parentName:"pre"},'{\n  "errorType": "Error",\n  "errorMessage": "Unable to determine event source based on event.",\n  "trace": [\n    "Error: Unable to determine event source based on event.",\n    "    at getEventSourceNameBasedOnEvent (/var/task/node_modules/@vendia/serverless-express/src/event-sources/utils.js:79:9)",\n    "    at proxy (/var/task/node_modules/@vendia/serverless-express/src/configure.js:37:51)",\n    "    at handler (/var/task/node_modules/@vendia/serverless-express/src/configure.js:95:12)",\n    "    at Runtime.handler (/var/task/node_modules/apollo-server-lambda/dist/ApolloServer.js:51:27)"\n  ]\n}\n')))),(0,n.kt)("h4",{id:"recommendation-3--graphene"},"Recommendation #3- ",(0,n.kt)("a",{parentName:"h4",href:"https://github.com/graphql-python/graphene"},"Graphene")),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Python library with 9000+ users for building GraphQL schemas/types. Since all ORCA lambdas are written in Python, using this library will make it easier for code changes."),(0,n.kt)("li",{parentName:"ul"},"Instead of writing GraphQL Schema Definition Language, developers will use Python code to describe the data provided by the server."),(0,n.kt)("li",{parentName:"ul"},"Can be deployed using lambda function with the help of ","[SAM]",(0,n.kt)("a",{parentName:"li",href:"https://github.com/ivanchoo/demo-aws-graphql-python/blob/master/template.yml"},"https://github.com/ivanchoo/demo-aws-graphql-python/blob/master/template.yml"),") or cloudformation. So serverless approach will charge when it is only used.")),(0,n.kt)("h5",{id:"practical-evaluation-2"},"Practical Evaluation"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"More flexible than other libraries; Would be much easier to switch DB technology.",(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},"Could use current database code."))),(0,n.kt)("li",{parentName:"ul"},"Deployed something using ",(0,n.kt)("a",{parentName:"li",href:"https://thomasstep.com/blog/graphene-and-lambda-functions"},"these basic instructions"),(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},"Can't access any form of UI."),(0,n.kt)("li",{parentName:"ul"},"Looking at code, UI/UI-Endpoints may not be present. Requires ",(0,n.kt)("inlineCode",{parentName:"li"},"query")," in Lambda input."),(0,n.kt)("li",{parentName:"ul"},"Without UI, doesn't have any advantage over building our own MS."),(0,n.kt)("li",{parentName:"ul"},"Filtering functions.",(0,n.kt)("pre",{parentName:"li"},(0,n.kt)("code",{parentName:"pre",className:"language-json"},'{\n  "query": "query doesnotmatter{ mirror(word: \\"apples\\") { backward } }"\n}\n')),(0,n.kt)("pre",{parentName:"li"},(0,n.kt)("code",{parentName:"pre",className:"language-json"},'{\n  "statusCode": 200,\n  "body": "{\\"mirror\\": {\\"backward\\": \\"selppa\\"}}"\n}\n'))),(0,n.kt)("li",{parentName:"ul"},'Errors are not properly communicated, instead returning 200 with a "null" body.',(0,n.kt)("ul",{parentName:"li"},(0,n.kt)("li",{parentName:"ul"},"Could be fixed with further development.")))))),(0,n.kt)("h3",{id:"graphql-ide"},"GraphQL IDE"),(0,n.kt)("p",null,"There are a few IDE that developers can use to interact with GraphQL API calls and query the server."),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/graphql/graphiql"},"GraphiQL"),". The live IDE can be seen ",(0,n.kt)("a",{parentName:"li",href:"http://graphql.org/swapi-graphql"},"here"),". "),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/graphql/graphql-playground"},"GraphQL Playground")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/andev-software/graphql-ide"},"GraphQL IDE"))),(0,n.kt)("h3",{id:"useful-tools"},"Useful tools"),(0,n.kt)("p",null,"The following tools might be useful for developers while working with GraphQL"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"GraphQL CLI- CLI for GraphQL development workflows."),(0,n.kt)("li",{parentName:"ul"},"GraphQL Docs- generates GraphQL documents. "),(0,n.kt)("li",{parentName:"ul"},"GraphDoc- generates GraphQL documents."),(0,n.kt)("li",{parentName:"ul"},"GraphQL Network- useful for debugging."),(0,n.kt)("li",{parentName:"ul"},"GraphQL Voyager- for visualizing data relations."),(0,n.kt)("li",{parentName:"ul"},"GraphQL Config- useful for configuring dev environment with GraphQL schema."),(0,n.kt)("li",{parentName:"ul"},"GraphQL Bindings- SDK for sharing GraphQL APIs"),(0,n.kt)("li",{parentName:"ul"},"GraphQL Boilerplates- useful for backend projects."),(0,n.kt)("li",{parentName:"ul"},"Apollo Graph Manager-  useful for monitoring the performance and usage of GraphQL backend.")),(0,n.kt)("h3",{id:"recommendation"},"Recommendation"),(0,n.kt)("p",null,"While GraphQL is an interesting technology, the lack of documentation makes implementation difficult.\nIn particular, deployment and integration lack vital instructions, with most tutorials running in a docker container or a Python script rather than a realistic environment.\nAt this time, I recommend not radically adjusting our architecture to work in a poorly documented and developed library, especially as we are likely to discover further pain-points.\nEven the one example that was functional in AWS had major flaws, such as a lack of proper error reporting, though this could be fixed with further development.\nSimply put, There would need to be significant research and development before our GraphQL functionality would reach our current level of database integration."),(0,n.kt)("h3",{id:"future-options"},"Future Options"),(0,n.kt)("p",null,"Should this be desired, I feel strongly that Graphene is the only known option that gives us the flexibility that is required to justify this level of adaptation.\nResearch would be required for:"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},"Ideal deployment method"),(0,n.kt)("li",{parentName:"ul"},"Accessing API + Error Codes"),(0,n.kt)("li",{parentName:"ul"},"Security"),(0,n.kt)("li",{parentName:"ul"},"GraphQL UI for use in development")),(0,n.kt)("p",null,"If the above are resolved, then Graphene would give slight benefits to output-filtering, but would not be any less code or any more maintainable than a centralized DB library."),(0,n.kt)("p",null,"Alternatively, GraphQL could theoretically be run in an EC2 instance managed by an orchestration service such as ",(0,n.kt)("a",{parentName:"p",href:"https://aws.amazon.com/fargate/?whats-new-cards.sort-by=item.additionalFields.postDateTime&whats-new-cards.sort-order=desc&fargate-blogs.sort-by=item.additionalFields.createdDate&fargate-blogs.sort-order=desc"},"Fargate")," with some form of connecting layer providing an API, but this is untested and would need research and cost analysis."),(0,n.kt)("h5",{id:"references"},"References"),(0,n.kt)("ul",null,(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://graphql.org/learn/queries/"},"https://graphql.org/learn/queries/")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/graphql-python"},"https://github.com/graphql-python")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/"},"https://www.altexsoft.com/blog/engineering/graphql-core-features-architecture-pros-and-cons/")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/core/index.html"},"https://hasura.io/docs/latest/graphql/core/index.html")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple"},"https://hasura.io/docs/latest/graphql/core/getting-started/docker-simple.html#docker-simple")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://www.moesif.com/blog/graphql/technical/Ways-To-Add-GraphQL-To-Your-Postgres-Database-Comparing-Hasura-Prisma-and-Others/"},"https://www.moesif.com/blog/graphql/technical/Ways-To-Add-GraphQL-To-Your-Postgres-Database-Comparing-Hasura-Prisma-and-Others/")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://docs.graphene-python.org/en/latest/quickstart/"},"https://docs.graphene-python.org/en/latest/quickstart/")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://github.com/ivanchoo/demo-aws-graphql-python"},"https://github.com/ivanchoo/demo-aws-graphql-python")),(0,n.kt)("li",{parentName:"ul"},(0,n.kt)("a",{parentName:"li",href:"https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse"},"https://git.earthdata.nasa.gov/projects/CMRQL/repos/hackfest-cmr-graphql/browse"))))}d.isMDXComponent=!0}}]);