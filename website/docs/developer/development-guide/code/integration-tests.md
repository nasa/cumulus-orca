---
id: integration-tests
title:  Integration Tests
description: Instructions on Developing and Running Integration Tests
---

While [unit tests](./unit-tests.md) cover individual functions, this does not constitute full coverage.
Consideration should be given to how the components of a large system interact, and how the layers fit together.
These tests run realistic scenarios against a full system via Bamboo scripts.

## Test Priorities

TODO

- Values should be randomized whenever possible.
  This will avoid copy-pasted strings causing false-positives.
  Only reuse resources when creating resources for each test would be problematic.
- The higher the level, the higher the priority.
  For example, testing a step function can theoretically cover the relevant lambdas along with their integration into the step function.
  Note that this does not fully cover the functionality of the individual components. Full run-through paths for each functionality of each component may be prohibitively time intensive both in terms of coding and test runtime, but should be considered.
- Smaller integration tests are better suited for narrowing in on errors, and should be considered for any new feature's [happy path](#happy-path).
- Due to automated processes and network latency, some operations may take time.
  Build retries with timeouts into network calls when appropriate.
- Since tests may take some time, test multiple values at once.
  For example, if testing a flow where different file extensions are treated differently, pass multiple types into the flow and make sure they are handled properly.

Some broad categories of tests are shown below.

### Happy Path

These are basic tests that perform a full run-through of a feature.
Randomized data is used to create a valid state, and a valid user is used to trigger/retrieve work.

### Security Paths

If feasible, there should be a copy of each [Happy Path](#happy-path) test that checks the same route, but with one property modified so as to fail security checks.
For lambdas with properly specified permissions, this will involve calling the lambda with a user that does not have permission to invoke the lambda.
For components such as databases and S3 buckets, this will involve attempting to retrieve/delete/add data with a user that does not have the appropriate permissions.

:::tip
To improve maintainability, use a shared function for setup of the [Happy Path](#happy-path) and Security Path tests for a given component.
:::

### Error Paths

These tests verify that when an error is expected, a proper error is returned/raised.
For example, several entries in our [API](../../../developer/api/api-gateway.md) should properly return a 404 error code if the entry does not exist in the database.
The test should fail if the API returns the error in a dictionary instead of an HTTP status code, or the API returns any other error code.

## What Not to Test

### External Integrations

We do not presently test integrations with Cumulus or other external consumers.
As we do not want to deepen coupling with Cumulus, it is best to focus on maintaining a consistent API.

## Needed Tests

This is a list of tests that should be created for existing Orca architecture. This list may change as tests are created and components are modified.

### [Internal Reconciliation](../../research/research-reconciliation.mdx)
- [Happy](#happy-path):
  1. Post randomized data to Orca catalog.
  1. Post S3 data in the structure of an S3 inventory report to the report bucket. Include at least one of each error type comparing between this and the catalog.
  1. Post a manifest to the report bucket.
  1. Retry calls to the [Internal Reconcile Report API](../../../developer/api/api-gateway.md/#internal-reconcile-report-jobs-api) until job is complete.
  1. Check that job is successful, and expected errors can be retrieved through the API.
     ::: warning
     If the catalog is not reset prior to this test, or other tests run in parallel, other errors may be present.
     Make sure none of these errors contain your randomized keys.
     :::
- [Security](#security-paths):
  1. Follow the Happy test up to contacting the API.
  1. No internal reconciliation endpoints should be publicly accessible, even if the job-id is known.
- [Error](#error-paths):
  1. Requests for a non-existent job and its reports should return HTTP Status 404.

### Ingest
- [Happy](#happy-path):
  1. Add files to an S3 bucket that is registered with Orca.
     Structure should imitate two granules.
  1. Call the OrcaCopyToGlacierWorkflow to ingest the granules to Orca.
  1. Retry calls to the [Catalog API](../../../developer/api/api-gateway.md/#catalog-reporting-api) until entries are found.
  1. Verify that the files are present in the proper Orca bucket.
- [Security](#security-paths):
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be publicly accessible, even if files are valid.
  1. Follow the Happy test up to contacting the API.
  1. No catalog endpoints should be publicly accessible, even if the granule-id or other values are known.
- [Error](#error-paths):
  1. Requests for catalog info on a non-existent granule/file should return HTTP Status 404.

### Recovery
- [Happy](#happy-path):
  1. Add files to an Orca backup bucket.
     Structure should imitate two granules.
  1. Call the OrcaRecoveryWorkflow to restore the files from Orca to another bucket.
  1. Retry calls to the [Recovery Granules API](../../../developer/api/api-gateway.md/#recovery-granules-api) until entries are found, and status is `complete`.
  1. Verify that the files are present in the proper Orca bucket.
- [Security](#security-paths):
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be publicly accessible, even if files are valid.
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be able to restore files to arbitrary buckets.
  1. Follow the Happy test up to contacting the API.
  1. No recovery endpoints should be publicly accessible, even if the granule-id or other values are known.
- [Error](#error-paths):
  1. Requests for recovery info on files that are not being recovered should return HTTP Status 404.

### General Security

All Orca resources should be private, baring specific exceptions carved out for customer integration.
Tests should be created that check for errors when contacting resources from a public perspective.
This applies to, among others:
- S3 Buckets
- Lambdas
- Databases
- Step Functions
- SQS Queues
- Secret Managers

:::note
Some of the above may be covered by other tests.
:::