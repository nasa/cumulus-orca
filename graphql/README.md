[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=graphql/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=graphql/requirements.txt)

**GraphQL Application**

Handles database queries for ORCA applications and users.

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.
Entry point is `src/adapters/webserver/main.py`, which will start the application at http://127.0.0.1:5000/graphql by default

- [Development](#development)
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

## Deployment
todo

### Environment Variables
- HOST
- PORT
- ORCA_ENV: Set to `Development` to enable dev-only features such as query-builder GUI and allowing queries via `GET`.
  

<a name="input-output-schemas"></a>
## Schemas
### Customer-Accessible Schemas
See [ORCA API Reference](https://nasa.github.io/cumulus-orca/docs/developer/api/orca-api) 
for customer-centric API documentation.
# todo: add recommendation to docs to ALWAYS request ErrorStrawberryTypeInterface with __typename and message properties

### Orca-Internal Schemas
todo

