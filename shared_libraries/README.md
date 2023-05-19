[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/shared_libraries/requirements-test.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/shared_libraries/requirements-test.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro)
for additional information on environment setup and testing.

# ORCA Shared Libraries

The ORCA shared libraries package contains several modules that group
common functionality used in ORCA lambda functions. Below is a list of
available libraries and their purpose.

- [**database**](API.md#orca_shared.database) - The database library contains several functions for connecting to and working with a database.
- [**recovery**](API.md#orca_shared.recovery) - The recovery library contains several functions used by ORCA recovery workflows.
- [**reconciliation**](API.md#orca_shared.reconciliation) - The reconciliation library contains information used by ORCA reconciliation workflows.


The following sections go into more detail on utilizing the libraries.

- [Installing ORCA Shared Libraries](#installing-orca-shared-libraries) - Information on installing the libraries into your application
- [Using ORCA Shared Libraries](#using-orca-shared-libraries) - Basic usage and documentation on the shared libraries.
- [Testing ORCA Shared Libraries](#testing-orca-shared-libraries) - Information on testing the shared libraries package.
- [Creating and Updating Shared Libraries](#creating-and-updating-shared-libraries) - Documentation on creating and updating shared libraries to use.


## Installing ORCA Shared Libraries

The ORCA shared libraries can be installed via `pip`. Users have the option of
installing all shared libraries or only select libraries needed for their application.
Since the package is not published on PyPI, users install the package by pointing
to the `shared_libraries` directory. This can be done with relative paths. To
install all shared libraries, run the following pip command.

:::info

The command below assumes you are running the installation from within the root repo
directory. Adjust the relative path accordingly based on where your requirements
file or install script is located.

:::

```bash
pip install ./shared_libraries/["all"]
```

If you only wish to install a specific library, denote that library during the
install. An example of installing only the shared database library can be seen
below.

```bash
pip install ./shared_libraries/["database"]
```


## Using ORCA Shared Libraries

To utilize the shared libraries, user's can import items at the package or module
level. To utilize all the functionality of a library import items at the package
level like the following.

```python
from orca_shared import database
```

To utilize a specific module the user can import just the objects available in
the module like the following.

```python
from orca_shared.database import shared_db
```

A complete listing of available packages and functions including usage is available
[here](API.md).


## Testing ORCA Shared Libraries

To run unit tests for ORCA shared libraries run the `bin/run_tests.sh` script from the
`tasks/shared_libraries` directory. Ideally, the tests should be run in a docker
container. The following shows setting up a container to run the tests.

```bash
# Invoke a docker container in interactive mode.
user$ docker run \
      -it \
      --rm \
      -v /path/to/cumulus-orca/repo:/data \
      amazonlinux:2 \
      /bin/bash

# Install the python development binaries
bash-4.2# yum install python3-devel

# In the container cd to /data
bash-4.2# cd /data

# Go to the task
bash-4.2# cd tasks/shared_libraries

# Run the tests
bash-4.2# bin/run_tests.sh
```

Note that Bamboo will run this same script via the `bin/run_tests.sh` script found
in the cumulus-orca base of the repo.


## Creating and Updating Shared Libraries

When creating or updating the shared libraries, there are additional updates that
should be made to ensure that the libraries are available and accessible to end
users. At a minimum the developer adjusting the shared libraries should perform
and validate the following items:

- Unit tests have been updated or added to address any changes and pass.
- The API documentation has been refreshed by running `bin/build_api.sh`
- If new library packages have been added or new third party libraries are needed,
  `setup.py` and `requirements.txt` has been updated with the new information.
- New library packages created have been added to `orca_shared/__init.py__` via `lazy_load`
- New library modules have been added to the proper packages `__init__.py` file.
- The value of `__version__` has been updated in the `orca_shared/__init__.py`'
  file to reflect a change using semantic versioning.
- This REAMDME has been updated with pertinent information.

