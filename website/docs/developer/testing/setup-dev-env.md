---
id: setup-dev-env
title: Setting Up a Dev Environment
description: Instructions on creating an environment for working with lambdas.
---

### Initial Setup
1. git clone https://github.com/nasa/cumulus-orca
1. Install [Python](https://www.python.org/downloads/) and restart if needed.
   Make sure Python is added to your PATH.
1. Install the AWS client.
    ```commandline
    pip3 install awscli
    ```

### Per-Lambda Setup
Lambdas should be built and tested within individual Virtual Environments.
1. Navigate to the task's folder within 'culumus-orca\tasks\[task name]'.
1. Create a new Virtual Environment and enter it.
   1. Windows:  
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
   1. Linux:  
      Create:
            ```
            todo
            ```  
      Activate:
            ```
            todo
            ```  
      Deactivate:
            ```
            todo
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