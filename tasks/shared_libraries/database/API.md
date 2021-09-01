# Table of Contents

* [shared\_db](#shared_db)
  * [get\_configuration](#shared_db.get_configuration)
  * [get\_admin\_connection](#shared_db.get_admin_connection)
  * [get\_user\_connection](#shared_db.get_user_connection)

<a name="shared_db"></a>
# shared\_db

Name: shared_db.py

Description: Shared library for database objects needed by the various libraries.

<a name="shared_db.get_configuration"></a>
#### get\_configuration

```python
get_configuration() -> Dict[str, str]
```

Create a dictionary of configuration values based on environment variables
parameter store information and other items needed to create the database.


```
Environment Variables:
    PREFIX (str): Deployment prefix used to pull the proper AWS secret.
    AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.

Parameter Store:
    <prefix>-orca-db-login-secret(string): The json string containing all the admin and user db login info.
```

**Arguments**:

  None
  

**Returns**:

- `Configuration` _Dict_ - Dictionary with all of the configuration information.
  The schema for the output is available [here](schemas/output.json).
  

**Raises**:

- `Exception` _Exception_ - When variables or secrets are not available.

<a name="shared_db.get_admin_connection"></a>
#### get\_admin\_connection

```python
get_admin_connection(config: Dict[str, str], database: str = None) -> Engine
```

Creates a connection engine to a database as a superuser.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
- `database` _str_ - Database for the admin user to connect to. Defaults to admin_database.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

<a name="shared_db.get_user_connection"></a>
#### get\_user\_connection

```python
get_user_connection(config: Dict[str, str]) -> Engine
```

Creates a connection engine to the application database as the application
database user.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

