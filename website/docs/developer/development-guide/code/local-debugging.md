---
id: local-debugging
title:  Local Debugging with AWS Resources
description: Instructions on Running Code Locally Against AWS Resources
---

Running and debugging code locally is a vital phase in the development and testing process.
Unfortunately, we do not currently have a method of simulating the cloud resources of AWS on a developer's machine.
The methods described below will give a developer machine access to AWS resources, which can be useful for testing input/output with real data and line-by-line debugging in the IDE of your choice.

- [Limitations](#limitations)
- [Setup](#setup)
- [Debugging Example](#debugging-example)

## Limitations
Note that this is not a replacement for integration testing.
Programs should still be deployed to a realistic AWS environment and run with realistic data to ensure that the methods described below do not grant an unexpected advantage/disadvantage to locally-run code.

This method also bypasses much of the AWS configuration and deployment steps.
Environment variables, Key-Value-Paris, and other inputs should be double-checked in AWS, especially if their function is internal to the program and otherwise invisible.

## Setup

This guide assumes that you have [deployed ORCA](../../deployment-guide/deployment-with-cumulus.md).
Cumulus components are largely unneeded, though the `PREFIX-CumulusECSCluster` EC2 Instance is required.
This EC2 Instance's 'Instance ID' can be identified using the AWS GUI or by running
```shell
aws ec2 describe-instances --filters Name=instance-state-name,Values=running Name=tag:Name,Values={PREFIX}-CumulusECSCluster --query "Reservations[*].Instances[*].InstanceId" --output text
```

Once the Instance ID is identified, run the following in a terminal. Be sure to replace `{Instance ID}`:
```shell
aws ssm start-session --target {Instance ID} --document-name AWS-StartPortForwardingSession --parameters portNumber=22,localPortNumber=6868
```

### Optional Setup
If you have deployed the RDS Database, and want to run code against it or check its contents via Aqua Data Studio, an extra step is required.
:::tip
AWS is inconsistent with naming. RDS 'Database' may also be called RDS 'Instance'
:::
First, retrieve the database's 'Endpoint'.
If you deployed via Cumulus' module, this is the 'rds_endpoint' output.
Otherwise, it can be found via the AWS GUI.

Run the following in an terminal. Be sure to replace `{DB Endpoint}` and `{Path to PREFIX-key-pair.pem}`:
```shell
ssh -p 6868 -L 5432:{DB Endpoint}:5432 -i "{Path to PREFIX-key-pair.pem}" -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ec2-user@127.0.0.1
```

## Debugging Example
After following the steps in [Setup Dev Env](setup-dev-env.md)

Ideally, developed code should isolate AWS configuration retrieval to a single function.
For example, the following code bypasses secret retrieval for quicker testing turnaround by calling `task` instead of the `handler` entry-point.

```python
import request_status_for_job

temp_db_connect_info = {
    "admin_database": "postgres",
    "admin_password": "An0th3rS3cr3t",
    "admin_username": "postgres",
    "host": "localhost",
    "port": "5432",
    "user_database": "PREFIX_orca",
    "user_password": "This1sAS3cr3t",
    "user_username": "PREFIX_orcauser",
}

print(request_status_for_job.task(
    "08c767d2-b4b9-4a05-9bc2-375038f33237",
    temp_db_connect_info))
```
