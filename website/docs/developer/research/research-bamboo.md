---
id: research-bamboo
title: Bamboo specs Research Notes
description: Research Notes on Bamboo CI/CD.
---

## Overview

[Bamboo](https://confluence.atlassian.com/bamboo/getting-started-with-bamboo-289277283.html) is a continuous integration (CI) and continuous deployment (CD) server used to automate the release and deployment of software applications. A typical bamboo workflow configuration consists of the following:

 - Plan - It consists of single or multiple stages that are run sequentially using the same repository and defines the build is triggered.
 - Stage - It consists of single or multiple jobs that run simultaneously.
 - Job - It processes one or more tasks that run simultaneously in an ordered fashion. 
 - Task - It is the actual work that is being executed as part of the build (e.g., running a shell script).

## Bamboo specs

Bamboo Specs are used to write Bamboo configuration as code either in Java or YAML and have corresponding plans/deployments created or updated automatically in Bamboo. YAML specs will be used in ORCA to convert Bamboo specs to code as its configuration is easy to understand. Check [documentation](https://docs.atlassian.com/bamboo-specs-docs/7.0.1/specs.html#starting-with-yaml) for details on the YAML specs.

:::note
A project has to be created manually first in Bamboo since it not possible to create a project with YAML file.
:::
An example of a bamboo config spec in YAML is shown below. This plan named `test-orca` consists of a manual stage named `orca test stage` which consists of a job named `orca test job`. This `orca test job` has a task that runs a shell script. 

```yaml
---
version: 2
plan:
  project-key: ORCA
  key: ORCA
  name: test-orca
stages:
- orca test stage:
    manual: true
    jobs:
    - orca test job
orca test job:
  key: OTJ
  tasks:
  - script:
      interpreter: SHELL
      scripts:
      - |-
        set -ex
        echo "hello"
```

### Bamboo configuration
Some of the important configuration parameters used to create a Bamboo plan is described below:

- Triggers- This is used to automatically run a bamboo plan. Users can specify how and when the build will be triggered. Some of the different types of triggers include repository polling, remote trigger, scheduled trigger, single day build trigger and tag trigger. Currently, ORCA uses `repository polling` trigger that polls source repository and builds when new changes are found. In this example, Bamboo will check the repository for changes every 60 seconds and automatically build it when changes are detected.

```yaml
triggers:
- polling:
    period: '60'
```

- Repositories- One or more repositories can be added to a plan, which will be available to every job in the plan. The first repository in the list is the plan’s default repository. An example of how a repository can be added to a bamboo plan is shown below. 

```yaml
repositories:
- ORCA repo:
    type: git
    url: https://github.com/nasa/cumulus-orca
    branch: develop
```
- Branches - Plan branches allow the user to run builds across different branches in the source repository using the same plan configuration.
In the example below, this pipeline will use the same plan when new branches are created in the repo and also link to a Jira issue if the branch name contains a Jira issue key.

```yaml
branches:
  create: for-new-branch
  delete:
    after-deleted-days: 7
    after-inactive-days: 30
  link-to-jira: true
```

- Variables- Variables are used to substitute values in the task config and inline scripts. To use in task scripts, use the syntax `${bamboo.variable_name}` and replace variable_name with yours. An example of using variables in a plan is shown below.
```yaml
variables:
  ORCA_VERSION: 0.0.1
  RELEASE_FLAG: 'false'
```
- Permissions- Permissions are used to restrict access to specific users to a Bamboo plan. In the following example, only the user rhassan can do some specific actions on this plan.

```yaml
version: 2
plan:
  key: ORCA
plan-permissions:
- users:
  - rhassan
  permissions:
  - view
  - edit
  - build
  - clone
  - admin
```
- Docker- It is also possible to run a job inside a docker image rather than the bamboo agent if required. Check this [documentation](https://hub.docker.com/r/atlassian/bamboo-agent-base) for more information.

```yaml
test job name:
  key: TJN
  docker:
    image: alpine
```
- Artifact- Artifacts are files created by a job build that can be used in other stages. An artifact definition can be created to specify which artifacts to keep and share from a build job. In the example below, an artifact definition named `test-artifact` is created under the job `test job` which is shared with other builds and deployments. Only the file matching the pattern .xml will be stored under artifact directory. 

```yaml
test job:
  artifacts:
  - name: test-artifact
    location: artifact
    pattern: '*.xml'
    shared: true
```
Check artifact [documentation](https://confluence.atlassian.com/bamboo/configuring-a-job-s-build-artifacts-289277071.html) for more information.

- Checkout- This is a task to check out a repository for use by just one job. In the example below, the job named `test job` has a checkout task that will checkout to the default repo defined in the plan before the tasks executes.

```yaml
test job:
  tasks:
  - checkout:
      description: Checkout Default Repository
```
Check this [documentation](https://confluence.atlassian.com/bamboo0800/checking-out-code-1077778795.html) for more information.


## Running Bamboo specs
In order to run the YAML definition file, it has to be stored at `bamboo-specs/bamboo.yml` or `bamboo-specs/bamboo.yaml`under the repository specified. Check this [documentation](https://confluence.atlassian.com/bamboo/bamboo-yaml-specs-938844479.html) for more information.

:::important
Make sure the linked repository have permissions to create plans within given project in order to execute the YAML definition and create a plan. 
:::


##### References
- https://confluence.atlassian.com/bamboo/understanding-the-bamboo-ci-server-289277285.html
- https://confluence.atlassian.com/bamboo/bamboo-yaml-specs-938844479.html
https://docs.atlassian.com/bamboo-specs-docs/7.0.1/specs.html