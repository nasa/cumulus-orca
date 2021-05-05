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
    post_to_database - Name: copy_files_to_archive.py

DESCRIPTION
    Description:  Lambda function that copies files from one s3 bucket
    to another s3 bucket.

CLASSES
    enum.Enum(builtins.object)
        RequestMethod
    
    class RequestMethod(enum.Enum)
     |  RequestMethod(value, names=None, *, module=None, qualname=None, type=None, start=1)
     |  
     |  An enumeration.
     |  
     |  Method resolution order:
     |      RequestMethod
     |      enum.Enum
     |      builtins.object
     |  
     |  Data and other attributes defined here:
     |  
     |  POST = <RequestMethod.POST: 'post'>
     |  
     |  PUT = <RequestMethod.PUT: 'put'>
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from enum.Enum:
     |  
     |  name
     |      The name of the Enum member.
     |  
     |  value
     |      The value of the Enum member.
     |  
     |  ----------------------------------------------------------------------
     |  Readonly properties inherited from enum.EnumMeta:
     |  
     |  __members__
     |      Returns a mapping of member name->value.
     |      
     |      This mapping lists all enum members, including aliases. Note that this
     |      is a read-only view of the internal mapping.

FUNCTIONS
    handler(event: Dict[str, List], context) -> None
        Lambda handler. Receives a list of queue entries from an SQS queue, and posts them to a database.
        
        Args:
            event: A dict with the following keys:
                'Records' (List): A list of dicts with the following keys:
                    'messageId' (str)
                    'receiptHandle' (str)
                    'body' (str): A json string representing a dict.
                        Contains key/value pairs of column names and values for those columns.
                    'attributes' (Dict)
                    'messageAttributes' (Dict): A dict with the following keys defined in the functions that write to queue.
                        'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
                        'TableName' (str): The name of the table to target.
            context: An object passed through by AWS. Used for tracking.
        Environment Vars: See requests_db.py's get_dbconnect_info for further details.
            'DATABASE_PORT' (int): Defaults to 5432
            'DATABASE_NAME' (str)
            'DATABASE_USER' (str)
            'PREFIX' (str)
            '{prefix}-drdb-host' (str, secretsmanager)
            '{prefix}-drdb-user-pass' (str, secretsmanager)
    
    insert_row_from_values(table_name: str, values: Dict[str, Any], db_connect_info: Dict) -> None
        Inserts a new row into the given table.
        
        Args:
            table_name: The name of the table to target.
            values: Contains key/value pairs of column names and values for those columns.
            db_connect_info: See requests_db.py's get_dbconnect_info for further details.
        
        Raises: database.DbError if error occurs when contacting database.
    
    send_record_to_database(record: Dict[str, Any], db_connect_info: Dict) -> None
        Deconstructs a record to its components and calls send_values_to_database with the result.
        
        Args:
            record: Contains the following keys:
                'body' (str): A json string representing a dict.
                    Contains key/value pairs of column names and values for those columns.
                'messageAttributes' (dict): Contains the following keys:
                    'TableName' (str): The name of the table to target.
                    'RequestMethod' (str): 'post' or 'put', depending on if row should be created or updated respectively.
            db_connect_info: See requests_db.py's get_dbconnect_info for further details.
    
    send_values_to_database(table_name: str, values: Dict[str, Any], request_method: post_to_database.RequestMethod, db_connect_info: Dict) -> None
        Args:
            table_name: The name of the table to target.
            values: Contains key/value pairs of column names and values for those columns.
            request_method: POST or PUT, depending on if row should be created or updated respectively.
            db_connect_info: See requests_db.py's get_dbconnect_info for further details.
    
    task(records: List[Dict[str, Any]], db_connect_info: Dict)
    
    update_row_in_table(table_name: str, table_keys: List[str], values: Dict[str, Any], db_connect_info: Dict) -> None
        Updates a row in the target table, using table_keys to identify the row that should be modified.
        
        Args:
            table_name: The name of the table to target.
            table_keys: A list of keys. Used to identify the row to change.
            values: Contains key/value pairs of column names and values for those columns.
                If a column name is in table_keys, the value will be used to identify the target row.
            db_connect_info: See requests_db.py's get_dbconnect_info for further details.
        
        Raises: database.DbError if error occurs when contacting database.

DATA
    Any = typing.Any
    Dict = typing.Dict
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
    table_key_dictionary = {'orca_recoverfile': ['job_id', 'granule_id', '...
```
