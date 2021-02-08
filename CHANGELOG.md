# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

### Changed

## [v2.0.1] 2021-2-5

### Changed
* *ORCA-125* BucketOwnerFullControl ACL is now set on for storage PUT requests in the copy_to_glacier lambda. This prevents errors during cross account (OU) copying of data.

## [v2.0.0] 2021-1-15

### Migration Notes
* *ORCA-67* The expected input/output of the copy_to_glacier lambda has been changed. See how to adopt these changes in
your Cumulus workflow [here](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_glacier).
* *ORCA-61* We now support collection-level configuration to exclude specific file-types from your glacier archive (when using
the copy_to_glacier lambda). See how to configure this for your collections [here](https://github.com/nasa/cumulus-orca/tree/master/tasks/copy_to_glacier#exclude-files-by-extension).

### Added
* *ORCA-58* ORCA user facing documentation
  * Docusaurus documentation website framework initialized and created
  * Initial content migrated off of wiki and into markdown pages for end users to view ORCA documentation with no wiki access.
  * Updates to README with starting the documentation server.
* *ORCA-61* Support dynamic configuration of files to exclude from glacier archive
  * Configured in a collection.meta configuration
* *ORCA-67* Generalize input/output scheme of copy_to_glacier lambda so it can be used more easily
in a Cumulus workflow.

### Changed
* *ORCA-68* Update DB tests to use mocking instead of real Postgres DB.
* *ORCA-70* As a DAAC we would like to be able to deploy multiple instances in our sandbox account.
  * Moves secret storage from SSM parameter store to secrets manager and adds a prefix to the keys.
* *ORCA-74* Move integration tests into their own files.


## [v1.0.0] 2020-12-4

### Migration Notes
None - this is the baseline release.

### Added
* *Misc*
  * Unit test upgrades - mocking unecessary dependencies.
  * Code formatting and styling
* *ORCA-65* Copy Lambda
  * We're including a copy lambda in the v1.0.0 release. The use of this lambda function is optional and explained in the task readme/documentation.
* *ORCA-33* Automated Building/Testing Updates
  * Created some bash scripts for use in the Bamboo build.
  * Updated requirements-dev.txt files for each task and moved the testing framework from nosetest (no longer supported) to coverage and pytest. 
  * Support in GitHub for automated build/test/release via Bamboo
  * Use `coverage` and `pytest` for coverage/testing

### Changed
