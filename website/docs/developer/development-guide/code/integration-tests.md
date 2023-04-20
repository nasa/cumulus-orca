---
id: integration-tests
title:  Integration Tests
description: Instructions on Developing and Running Integration Tests
---

While [unit tests](./unit-tests.md) cover individual functions, this does not constitute full coverage.
Consideration should be given to how the components of a large system interact, and how the layers fit together.
These tests run realistic scenarios against a full system via scripts run in Bamboo.

- [File Structure](#structure)
- [Running Tests](#running)

<a name="structure"></a>

## File Structure

Tests are grouped into modules under the `test_packages` folder.
When adding a test group:
1. Create a new directory under `test_packages`, named appropriately for your new group.
2. Copy the `__init__.py` from another group into your group.
3. Modify the `workflow_tests/__init__.py`, adding your new group to the list of imports.
4. You may now begin adding test files to your new directory.
   Note that each filename should begin with the `test` prefix, and should contain a class of the format `class TestDescriptiveName(TestCase):`

:::note
As tests are run in parallel, it is generally good practice to have one test-per-file, to avoid any shared setup.
:::

<a name="running"></a>

## Running Tests

### Running Locally
1. [Deploy ORCA to AWS](https://nasa.github.io/cumulus-orca/docs/developer/deployment-guide/deployment).
2. Connect to the NASA vpn.
3. Set the following environment variables:
   1. `orca_API_DEPLOYMENT_INVOKE_URL` Output from the ORCA TF module. ex: `https://0000000000.execute-api.us-west-2.amazonaws.com`
   2. `orca_COPY_TO_ARCHIVE_STEP_FUNCTION_ARN` ARN of the copy_to_archive step function. ex: `arn:aws:states:us-west-2:000000000000:stateMachine:PREFIX-OrcaCopyToArchiveWorkflow`
   3. `orca_RECOVERY_BUCKET_NAME` S3 bucket name where the recovered files will be archived. ex: `test-orca-primary`
4. 
   Get your Cumulus EC2 instance ID using the following AWS CLI command using your `<PREFIX>`.
   ```shell
   aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values={PREFIX}-CumulusECSCluster --query "Reservations[*].Instances[*].InstanceId" --output text
   ```
   Then run the following bash command, 
   replacing `i-00000000000000000` with your `PREFIX-CumulusECSCluster` ec2 instance ID, 
   and `0000000000.execute-api.us-west-2.amazonaws.com` with your API Gateway identifier:

   ```shell
   aws ssm start-session --target i-00000000000000000 --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters '{"host":["0000000000.execute-api.us-west-2.amazonaws.com"],"portNumber":["443"], "localPortNumber":["8000"]}'
   ```
5. In the root folder `workflow_tests`, run the following command:
   ```shell
   bin/run_tests.sh
   ```
### Running in Bamboo
[Not yet developed.](https://bugs.earthdata.nasa.gov/browse/ORCA-96)

## Test Assumptions

These are suggestions for rules and setup procedures for integration tests.
Documentation below assumes that the following are applied.

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
- A persistent data bucket should exist to provide files for ingest.
- Tests should be run in parallel when possible.
- Use realistic routes when feasible. For example, ingest files to Orca instead of placing them in the bucket manually.
- All resources, including storage mediums, should be deleted after all tests have been run.
  :::warning
  When deleted, KMS keys persist for a minimum of 7 days. In order to run tests more often 
  than every 7-8 days, a randomized prefix could be used for   deployment to avoid collision
  errors with KMS key names within the same environment.
  :::
- Initially, automated validation will not include checking Cloudwatch logs. Logs will be available for 7 days to help manually identify any errors and troubleshoot problems. In the future, automating searches for key phrases in Cloudwatch logs as validation may be used for identifying point-of-failure in processes.
- Integration tests should be run on a regular cadence. Initial suggestion is once every 1-2 weeks.
- Ingest tests only work if the catalog is cleaned between runs. Make sure to remove the recovered files from your orca recovery bucket as well as catalog after running the tests.

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

:::warning
Due to how NGAP handles security, even resources with public access enabled cannot be accessed publicly.
Further research should be done to identify how to perform these tests.
:::

### Error Paths

These tests verify that when an error is expected, a proper error is returned/raised.
For example, several entries in our [API](../../../developer/api/api.md) should properly return a 404 error code if the entry does not exist in the database.
The test should fail if the API returns the error in a dictionary instead of an HTTP status code, or the API returns any other error code.

## What Not to Test

### External Integrations

We do not presently test integrations with Cumulus or other external consumers.
As we do not want to deepen coupling with Cumulus, it is best to focus on maintaining a consistent API.

Manual tests should still be run with Cumulus to check for changes in Cumulus output/input schemas, Orca input/output schemas, Cumulus Message Adapter, and the Cumulus Dashboard. These manual tests should replicate the ingest/recovery tests.

### Performance

While there is a desire to eventually develop performance tests, these tests should focus on functionality with generous timeouts.

## Needed Tests

This is a list of tests that should be created for existing Orca architecture. This list may change as tests are created and components are modified.

### [Internal Reconciliation](../../research/research-reconciliation.mdx)
- [Happy](#happy-path):
  1. Ingest randomized data to Orca.
  1. Modify the catalog and post S3 data in the structure of an S3 inventory report to the report bucket. Include at least one of each error type comparing between the two sources.
     :::note
     While we could wait for the automated S3 Inventory report to generate, this could take up to 24 hours, which would delay testing.
     Therefore, use a dummy report that matches the AWS report schema to perform automated testing.
     Prior to release or periodically, an S3 Inventory report should be generated through AWS mechanisms to validate the schema and style of the test report being used.
     :::
  1. Post a mocked-up manifest to the report bucket.
  1. Retry calls to the [Internal Reconcile Report API](../../../developer/api/api.md/#internal-reconcile-report-jobs-api) until job is complete.
  1. Check that job is successful, and expected errors can be retrieved through the API.
     :::warning
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
     Structure should imitate multiple granules.
     :::tip
     Include a large (bigger than 250 Gb) file to make sure timeouts do not prevent ingest.
     :::
     :::tip
     Test ingesting from Glacier buckets as well as regular buckets.
     Make sure that Glacier data is less than 24 hours old.
     If older, data will be moved out of `recovered` and `pre-archival` states, and ingest will incur additional costs and time penalties, possibly beyond timeout limits.
     :::
  1. Call the OrcaCopyToArchiveWorkflow to ingest the granules to Orca.
     :::tip
     Make sure to cover excludedFileExtensions being set, being unset, and excluding/allowing proper files in either case.
     May require additional tests.
     :::
     :::tip
     Future work will allow us to target multiple buckets with ingest.
     :::
  1. Check the StepFunction status until status is completed.
  1. Call the [Catalog API](../../../developer/api/api.md/#catalog-reporting-api) to make sure entries are found.
  1. Verify that the files are present in the proper Orca bucket.
- [Security](#security-paths):
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be publicly accessible, even if files are valid.
  1. Follow the Happy test up to contacting the API.
  1. No catalog endpoints should be publicly accessible, even if the granule-id or other values are known.
- [Error](#error-paths):
  1. Requests for catalog info on a non-existent granule/file should return HTTP Status 404.

  1. Attempting to ingest a file that does not exist should result in `files does not exist`.

### Recovery
- [Happy](#happy-path):
  1. Ingest randomized data to Orca.
     :::tip
     Include a large (bigger than 250 Gb) file to make sure timeouts do not prevent recovery.
     :::
  1. Call the OrcaRecoveryWorkflow to restore the files from Orca to another bucket.
     :::tip
     Make sure to cover excludedFileExtensions being set, being unset, and excluding/allowing proper files in either case.
     May require additional tests.
     Ignored files will not be listed in output.
     :::
  1. Retry calls to the [Recovery Granules API](../../../developer/api/api.md/#recovery-granules-api) until entries are found, and status is `complete`.
     :::warning
     Recovery may take up to 4 hours.
     :::
  1. Verify that the files are present in the proper target bucket.
- [Security](#security-paths):
  1. Follow the Happy test up to contacting the API.
  1. No recovery endpoints should be publicly accessible, even if the granule-id or other values are known.

  :::tip
  The following test will only be valid after completing [ORCA-351](https://bugs.earthdata.nasa.gov/browse/ORCA-351).
  :::
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be publicly accessible, even if files are valid.
  1. Follow the Happy test up to calling the workflow.
  1. Workflow should not be able to restore files to arbitrary buckets that Orca does not have permission to write to.
- [Error](#error-paths):
  1. Requests for recovery info on files that are not being recovered should return HTTP Status 404.

  1. Recovering files that are in the process of being recovered should return an error.

  1. Attempting to recover a file that does not exist should result in `files does not exist`.

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