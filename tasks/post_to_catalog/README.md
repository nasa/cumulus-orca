[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/post_to_catalog/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/post_to_catalog/requirements.txt)

**Lambda function post_to_catalog **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
- [pydoc post_to_catalog](#pydoc)

<a name="deployment"></a>
## Deployment
```
    see /bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="pydoc"></a>
## pydoc post_to_catalog
```
Help on module post_to_catalog:

NAME
    post_to_catalog - Name: post_to_catalog.py

DESCRIPTION
    Description:  Pulls entries from a queue and posts them to a DB.

FUNCTIONS
    create_catalog_records(provider: Dict[str, str], collection: Dict[str, str], granule: Dict[str, Union[str, List[Dict[str, Union[str, int]]]]], engine: sqlalchemy.future.engine.Engine) -> None
        Posts the information to the catalog database.
        
        Args:
            provider: See schemas/catalog_record_input.json.
            collection: See schemas/catalog_record_input.json.
            granule: See schemas/catalog_record_input.json.
            engine: The sqlalchemy engine to use for contacting the database.
    
    create_collection_sql()
    
    create_file_sql()
    
    create_granule_sql()
    
    create_provider_sql()
    
    dummy()
    
    handler(event: Dict[str, List], context) -> None
        Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.
        
        Args:
            event: A dict with the following keys:
                'Records' (List): A list of dicts with the following keys:
                    'messageId' (str)
                    'receiptHandle' (str)
                    'body' (str): A json string representing a dict.
                        See catalog_record_input in schemas for details.
            context: An object passed through by AWS. Used for tracking.
        Environment Vars: See shared_db.py's get_configuration for further details.
            'DATABASE_PORT' (int): Defaults to 5432
            'DATABASE_NAME' (str)
            'APPLICATION_USER' (str)
            'PREFIX' (str)
            '{prefix}-drdb-host' (str, secretsmanager)
            '{prefix}-drdb-user-pass' (str, secretsmanager)
    
    send_record_to_database(record: Dict[str, Any], engine: sqlalchemy.future.engine.Engine) -> None
        Deconstructs a record to its components and calls create_catalog_records with the result.
        
        Args:
            record: Contains the following keys:
                'body' (str): A json string representing a dict.
                    Contains key/value pairs of column names and values for those columns.
                    Must match catalog_record_input.json.
            engine: The sqlalchemy engine to use for contacting the database.
    
    task(records: List[Dict[str, Any]], db_connect_info: Dict) -> None
        Sends each individual record to send_record_to_database.
        
        Args:
            records: A list of Dicts. See send_record_to_database for schema info.
            db_connect_info: See shared_db.py's get_configuration for further details.

DATA
    Any = typing.Any
    Dict = typing.Dict
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    Union = typing.Union
    raw_schema = <_io.TextIOWrapper name='schemas/catalog_record_input.jso...
```
