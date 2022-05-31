---
id: setup-dev-env
title: Setting Up a Dev Environment
description: Instructions on creating an environment for working with lambdas.
---

## Initial Setup
1. Familiarize yourself with [contributing to these documents](../documentation/documentation-intro.md) prior to modifying/testing code.
   Updating documentation is a shared responsibility.
1. git clone https://github.com/nasa/cumulus-orca
1. Install [Python 3.8.X](https://www.python.org/downloads/) and restart if needed.
   Make sure Python is added to your PATH.
1. Install the AWS client. View the [official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) if needed.
    ```commandline
    pip3 install awscli
    ```
1. [Install and Configure git-secrets](https://wiki.earthdata.nasa.gov/display/ESKB/Install+and+Configure+git-secrets)

## Per-Lambda Setup
Lambdas should be built and tested within individual Virtual Environments.
1. Navigate to the task's folder within 'culumus-orca\tasks\[task name]'.
1. Create and activate a new Python [Virtual Environment](https://docs.python.org/3.8/library/venv.html).
   1. Windows Command Line:  
      Create:
            ```
            python -m venv venv
            ```  
      Activate:
            ```
            venv\Scripts\activate
            ```  
      Deactivate:
            ```
            venv\Scripts\deactivate.bat
            ```
   1. Linux/[Cmder](https://cmder.net/):  
      Create:
            ```
            python -m venv venv
            ```  
      Activate:
            ```
            source venv/bin/activate
            ```  
      Deactivate:
            ```
            deactivate
            ```
1. With the VEnv activated, install requirements.
   ```commandline
   pip install boto3
   pip install -r requirements.txt
   ```
1. Install additional development requirements.
   ```commandline
   pip install coverage
   pip install pylint
   pip install -r requirements-dev.txt
   ```