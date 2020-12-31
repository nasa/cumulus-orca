# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
* *ORCA-58* ORCA user facing documentation
  * Docusaurus documentation website framework initialized and created
  * Intial content migrated off of wiki and into markdown pages for end users to view ORCA documentation with no wiki access.
  * Updates to README with starting the documentation server.


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
