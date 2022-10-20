# Table of Contents

* [post\_to\_catalog](#post_to_catalog)
  * [task](#post_to_catalog.task)
  * [send\_record\_to\_database](#post_to_catalog.send_record_to_database)
  * [create\_catalog\_records](#post_to_catalog.create_catalog_records)
  * [handler](#post_to_catalog.handler)

<a id="post_to_catalog"></a>

# post\_to\_catalog

Name: post_to_catalog.py

Description:  Pulls entries from a queue and posts them to a DB.

<a id="post_to_catalog.task"></a>

#### task

```python
def task(records: List[Dict[str, Any]], db_connect_info: Dict) -> None
```

Sends each individual record to send_record_to_database.

**Arguments**:

- `records` - A list of Dicts. See send_record_to_database for schema info.
- `db_connect_info` - See shared_db.py's get_configuration for further details.

<a id="post_to_catalog.send_record_to_database"></a>

#### send\_record\_to\_database

```python
def send_record_to_database(record: Dict[str, Any], engine: Engine) -> None
```

Deconstructs a record to its components and calls create_catalog_records with the result.

**Arguments**:

- `record` - Contains the following keys:
- `'body'` _str_ - A json string representing a dict.
  Contains key/value pairs of column names and values for those columns.
  Must match catalog_record_input.json.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="post_to_catalog.create_catalog_records"></a>

#### create\_catalog\_records

```python
@retry_operational_error()
def create_catalog_records(provider: Dict[str, str], collection: Dict[str,
                                                                      str],
                           granule: Dict[str, Union[str,
                                                    List[Dict[str,
                                                              Union[str,
                                                                    int]]]]],
                           engine: Engine) -> None
```

Posts the information to the catalog database.

**Arguments**:

- `provider` - See schemas/catalog_record_input.json.
- `collection` - See schemas/catalog_record_input.json.
- `granule` - See schemas/catalog_record_input.json.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="post_to_catalog.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, List], context: LambdaContext) -> None
```

Lambda handler. Receives a list of queue entries from an SQS queue,
and posts them to a database.

**Arguments**:

- `event` - A dict with the following keys:
- `'Records'` _List_ - A list of dicts with the following keys:
  'messageId' (str)
  'receiptHandle' (str)
- `'body'` _str_ - A json string representing a dict.
  See catalog_record_input in schemas for details.
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  Environment Vars:
  DB_CONNECT_INFO_SECRET_ARN (string):
  Secret ARN of the AWS secretsmanager secret for connecting to the database.
  See shared_db.py's get_configuration for further details.

