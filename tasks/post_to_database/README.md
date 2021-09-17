[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_database/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/post_to_database/requirements.txt)

**Lambda function post_to_database **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc post_to_database](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc post_to_database
```
Help on module post_to_database:

NAME
    post_to_database - Name: post_to_database.py

DESCRIPTION
    Description:  Pulls entries from a queue and posts them to a DB.

FUNCTIONS
    create_file_sql()
    
    create_job_sql()
    
    create_status_for_job_and_files(job_id: str, granule_id: str, request_time: str, archive_destination: str, files: List[Dict[str, Any]], engine: sqlalchemy.future.engine.Engine) -> None
        Posts the entry for the job, followed by individual entries for each file.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            archive_destination: The S3 bucket destination of where the data is archived.
            request_time: The time the restore was requested in utc and iso-format.
            files: A List of Dicts with the following keys:
                'filename' (str)
                'key_path' (str)
                'restore_destination' (str)
                'status_id' (int)
                'error_message' (str, Optional)
                'request_time' (str)
                'last_update' (str)
                'completion_time' (str, Optional)
            engine: The sqlalchemy engine to use for contacting the database.
    
    handler(event: Dict[str, List], context) -> None
        Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.
        
        Args:
            event: A dict with the following keys:
                'Records' (List): A list of dicts with the following keys:
                    'messageId' (str)
                    'receiptHandle' (str)
                    'body' (str): A json string representing a dict.
                        See files in schemas for details.
                    'attributes' (Dict)
                    'messageAttributes' (Dict): A dict with the following keys defined in the functions that write to queue.
                        'RequestMethod' (str): Matches to a shared_recovery.RequestMethod.
            context: An object passed through by AWS. Used for tracking.
        Environment Vars: See shared_db.py's get_configuration for further details.
            'DATABASE_PORT' (int): Defaults to 5432
            'DATABASE_NAME' (str)
            'APPLICATION_USER' (str)
            'PREFIX' (str)
            '{prefix}-drdb-host' (str, secretsmanager)
            '{prefix}-drdb-user-pass' (str, secretsmanager)
    
    send_record_to_database(record: Dict[str, Any], engine: sqlalchemy.future.engine.Engine) -> None
        Deconstructs a record to its components and calls send_values_to_database with the result.
        
        Args:
            record: Contains the following keys:
                'body' (str): A json string representing a dict.
                    Contains key/value pairs of column names and values for those columns.
                    Must match one of the schemas.
                'messageAttributes' (dict): Contains the following keys:
                    'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
            engine: The sqlalchemy engine to use for contacting the database.
    
    task(records: List[Dict[str, Any]], db_connect_info: Dict) -> None
        Sends each individual record to send_record_to_database.
        
        Args:
            records: A list of Dicts. See send_record_to_database for schema info.
            db_connect_info: See shared_db.py's get_configuration for further details.
    
    update_file_sql()
    
    update_job_sql()
    
    update_status_for_file(job_id: str, granule_id: str, filename: str, last_update: str, completion_time: Union[str, NoneType], status_id: int, error_message: Union[str, NoneType], engine: sqlalchemy.future.engine.Engine) -> None
        Updates a given file's status entry, modifying the job if all files for that job have advanced in status.
        
        Args:
            job_id: The unique identifier used for tracking requests.
            granule_id: The id of the granule being restored.
            filename: The name of the file being copied.
            last_update: The time this status update occurred, in UTC iso-format.
            completion_time: The completion time, in UTC iso-format.
            status_id: Defines the status id used in the ORCA Recovery database.
            error_message: message displayed on error.
        
            engine: The sqlalchemy engine to use for contacting the database.

DATA
    Any = typing.Any
    Dict = typing.Dict
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    Optional = typing.Optional
    raw_schema = <_io.TextIOWrapper name='schemas/update_file_input.json' ...
```
