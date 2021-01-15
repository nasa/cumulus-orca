---
id: setup-dev-env
title: Setting Up a Dev Environment
description: Instructions on creating an environment for working with lambdas.
---

## Initial Setup
1. git clone https://github.com/nasa/cumulus-orca
1. Install [Python 3.8.X](https://www.python.org/downloads/) and restart if needed.
   Make sure Python is added to your PATH.
1. Install the AWS client. View the [official documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) if needed.
    ```commandline
    pip3 install awscli
    ```

## Per-Lambda Setup
Lambdas should be built and tested within individual Virtual Environments.
1. Navigate to the task's folder within 'culumus-orca\tasks\[task name]'.
1. Create a new Virtual Environment and enter it.
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
            source venv\Scripts\activate
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
   If requirements.txt references db_dbutils and/or pg_utils, install them with their respective commands.
   ```commandline
   pip install ..\dr_dbutils\dist\dr_dbutils-1.0.tar.gz
   pip install ..\pg_utils\dist\pg_utils-1.0.tar.gz
   ```
1. If you are going to develop code, install development requirements.
   ```commandline
   pip install coverage
   pip install pylint
   pip install -r requirements-dev.txt
   ```