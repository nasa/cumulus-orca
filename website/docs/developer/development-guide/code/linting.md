---
id: linting
title: Running Pylint Against Your Code
description: Instructions on running PyLint.
---

[Pylint](https://www.pylint.org/) is a best-practice analysis 
tool that is used to flag coding errors, including, but not 
limited to, false-positives, syntax errors, and style errors 
in Python. Pylint follows the style recommended by the 
[Python style guide or PEP 8](https://www.python.org/dev/peps/pep-0008/).

:::tip

Run through the steps in [Setting Up a Dev Environment](setup-dev-env.md) prior to modifying/testing code.

:::


Visit [here](https://code.visualstudio.com/docs/python/linting) for an
article on Linting Python in Visual Studio Code. The article provides
information on the following Pylint topics:

* [Enable linters](https://code.visualstudio.com/docs/python/linting#_enable-linters)
* [Disable linting](https://code.visualstudio.com/docs/python/linting#_disable-linting)
* [Run linting](https://code.visualstudio.com/docs/python/linting#_disable-linting)
* [General linting settings](https://code.visualstudio.com/docs/python/linting#_general-linting-settings)
* [Specific linters](https://code.visualstudio.com/docs/python/linting#_specific-linters)
* [Pylint](https://code.visualstudio.com/docs/python/linting#_pylint)
* [pydocstyle](https://code.visualstudio.com/docs/python/linting#_pydocstyle)
* [pycodestyle (pep8)](https://code.visualstudio.com/docs/python/linting#_pycodestyle-pep8)
* [Prospector](https://code.visualstudio.com/docs/python/linting#_prospector)
* [Flake8](https://code.visualstudio.com/docs/python/linting#_flake8)
* [mypy](https://code.visualstudio.com/docs/python/linting#_mypy)
* [Troubleshooting linting](https://code.visualstudio.com/docs/python/linting#_troubleshooting-linting)



## Manually Running PyLint
1. Navigate to the task's base folder.
1. Activate the virtual environment.
1. Run pylint and fix any discovered issues if you can.
   ```commandline
   pylint [file name]
   ```
