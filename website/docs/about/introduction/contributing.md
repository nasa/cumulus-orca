---
id: intro-contributing
title: Contributing to ORCA
description: Provides high level information on contributing to the ORCA project.
---
# Types of Contributors
## Engagement Levels
ORCA has several ways to engage with the project and several different
engagement levels. The various levels are explained below.

**Advisor:**  Stakeholders that would like to be invited to demos and
provide input on where the system is headed. This includes active engagement
in the [ORCA Working Group](https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Working+Group).

**DAAC Integrator:**  Developers, engineers, and operators that implement
ORCA into their DAAC workflows and Cumulus instances.

**Contributor:**  Developers, engineers, and users who are not a
part of the core team that actively provides fixes, enhancements,
and features through code pull requests to the cumulus-orca
repository.

**Core Developer:**  Part of the core ORCA team that develops code and
documentation for the ORCA components. If you would like to be a part of
this team, please contact [Darla Werner](mailto:dwerner@contractor.usgs.gov?subject=Join%20ORCA%20Core%20Development%20Team).


## Requesting Fixes, Enhancements, and Features
Feature requests and bug documentation should be done by filling out a Jira
card in the [ORCA Jira project](https://bugs.earthdata.nasa.gov/secure/RapidBoard.jspa?rapidView=985&projectKey=ORCA&view=planning.nodetail).
Please create a descriptive card on the backlog detailing the feature or
bug along with the desired outcome for acceptance criteria. When possible,
include contact information should the team have questions about the issue.
Prior to creating a card, please verify that a card does not already exist
in the project. If a card does exist, add a comment to the card so that the
team knows the additional impact for the feature or bug.

All cards are prioritized and worked on in a normal 2-week sprint cycle
that follows the EOSDIS SAFe timelines.

## Providing Fixes, Enhancements, and Features
ORCA contributors may provide fixes, enhancements, and features to the ORCA
project. When making changes to code, ORCA follows a branching model
similar to this [git branching model](https://nvie.com/posts/a-successful-git-branching-model/).

In general, you must create a feature branch off of the develop branch, make
changes on that branch, push the branch to the repo, and submit a pull
request for approval. When creating your pull request, you will select your
branch as the source and the branch develop as the destination. The pull
request will give ORCA core developers time to review the changes and offer
suggestions. All approved pull requests will be merged into the develop
branch and be in a release at some later time. Feature branches should be
named feature/[ORCA Jira Card ID].

Here is an example of creating a feature branch.

### Creating a feature branch

```bash
git clone https://github.com/nasa/cumulus-orca.git

cd cumulus-orca

git checkout develop

git checkout -b feature/ORCA-1234 develop

git push origin feature/ORCA-1234
```

