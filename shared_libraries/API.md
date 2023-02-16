# Table of Contents

* [orca\_shared](#orca_shared)
* [orca\_shared.reconciliation.test.unit\_tests.test\_shared\_reconciliation](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation)
  * [TestSharedReconciliationLibraries](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries)
    * [test\_get\_partition\_name\_from\_bucket\_name\_happy\_path](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_get_partition_name_from_bucket_name_happy_path)
    * [test\_update\_job\_happy\_path](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_happy_path)
    * [test\_update\_job\_error\_message\_required\_on\_error\_status](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_error_message_required_on_error_status)
    * [test\_update\_job\_error\_message\_only\_valid\_on\_error\_status](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_error_message_only_valid_on_error_status)
    * [test\_internal\_update\_job\_error\_logged\_and\_raised](#orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_internal_update_job_error_logged_and_raised)
* [orca\_shared.reconciliation](#orca_shared.reconciliation)
* [orca\_shared.reconciliation.shared\_reconciliation](#orca_shared.reconciliation.shared_reconciliation)
  * [OrcaStatus](#orca_shared.reconciliation.shared_reconciliation.OrcaStatus)
  * [get\_partition\_name\_from\_bucket\_name](#orca_shared.reconciliation.shared_reconciliation.get_partition_name_from_bucket_name)
  * [update\_job](#orca_shared.reconciliation.shared_reconciliation.update_job)
  * [internal\_update\_job](#orca_shared.reconciliation.shared_reconciliation.internal_update_job)
* [orca\_shared.database.test.unit\_tests.adapters](#orca_shared.database.test.unit_tests.adapters)
* [orca\_shared.database.test.unit\_tests.adapters.api.test\_aws](#orca_shared.database.test.unit_tests.adapters.api.test_aws)
  * [TestAWS](#orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS)
    * [setUp](#orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.setUp)
    * [test\_get\_configuration\_happy\_path](#orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_happy_path)
    * [test\_get\_configuration\_no\_aws\_region](#orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_no_aws_region)
    * [test\_get\_configuration\_bad\_secret](#orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_bad_secret)
* [orca\_shared.database.test.unit\_tests.adapters.api](#orca_shared.database.test.unit_tests.adapters.api)
* [orca\_shared.database.test.unit\_tests.use\_cases.test\_validation](#orca_shared.database.test.unit_tests.use_cases.test_validation)
  * [TestCreatePostgresConnectionUri](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri)
    * [test\_validate\_config\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_config_happy_path)
    * [test\_validate\_password\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_happy_path)
    * [test\_validate\_password\_short\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_short_raises_error)
    * [test\_validate\_password\_number\_missing\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_number_missing_raises_error)
    * [test\_validate\_password\_upper\_case\_missing\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_upper_case_missing_raises_error)
    * [test\_validate\_password\_lower\_case\_missing\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_lower_case_missing_raises_error)
    * [test\_validate\_password\_special\_character\_missing\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_special_character_missing_raises_error)
    * [test\_validate\_postgres\_name\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_happy_path)
    * [test\_validate\_postgres\_name\_short\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_short_raises_error)
    * [test\_validate\_postgres\_name\_long\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_long_raises_error)
    * [test\_validate\_postgres\_name\_invalid\_raises\_error](#orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_invalid_raises_error)
* [orca\_shared.database.test.unit\_tests.use\_cases](#orca_shared.database.test.unit_tests.use_cases)
* [orca\_shared.database.test.unit\_tests.use\_cases.test\_create\_postgres\_connection\_uri](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri)
  * [TestCreatePostgresConnectionUri](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri)
    * [test\_create\_user\_uri\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_user_uri_happy_path)
    * [test\_create\_admin\_uri\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_admin_uri_happy_path)
    * [test\_create\_admin\_uri\_overwrite\_database](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_admin_uri_overwrite_database)
    * [test\_\_create\_connection\_uri\_happy\_path](#orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test__create_connection_uri_happy_path)
* [orca\_shared.database.test.unit\_tests.test\_shared\_db](#orca_shared.database.test.unit_tests.test_shared_db)
  * [TestSharedDatabaseLibraries](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries)
    * [setUp](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.setUp)
    * [tearDown](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.tearDown)
    * [test\_get\_configuration\_happy\_path](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_happy_path)
    * [test\_get\_configuration\_no\_aws\_region](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_no_aws_region)
    * [test\_get\_configuration\_bad\_secret](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_bad_secret)
    * [test\_get\_admin\_connection\_database\_values](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_admin_connection_database_values)
    * [test\_get\_user\_connection\_database\_values](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_user_connection_database_values)
    * [test\_\_create\_connection\_call\_values](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test__create_connection_call_values)
    * [test\_retry\_operational\_error\_non\_operational\_error\_raises](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_retry_operational_error_non_operational_error_raises)
    * [test\_retry\_operational\_error\_operational\_error\_retries\_and\_raises](#orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_retry_operational_error_operational_error_retries_and_raises)
* [orca\_shared.database.shared\_db](#orca_shared.database.shared_db)
  * [get\_configuration](#orca_shared.database.shared_db.get_configuration)
  * [get\_admin\_connection](#orca_shared.database.shared_db.get_admin_connection)
  * [get\_user\_connection](#orca_shared.database.shared_db.get_user_connection)
  * [retry\_operational\_error](#orca_shared.database.shared_db.retry_operational_error)
* [orca\_shared.database](#orca_shared.database)
* [orca\_shared.database.adapters](#orca_shared.database.adapters)
* [orca\_shared.database.adapters.api](#orca_shared.database.adapters.api)
* [orca\_shared.database.adapters.api.aws](#orca_shared.database.adapters.api.aws)
  * [get\_configuration](#orca_shared.database.adapters.api.aws.get_configuration)
* [orca\_shared.database.use\_cases.create\_postgres\_connection\_uri](#orca_shared.database.use_cases.create_postgres_connection_uri)
  * [create\_user\_uri](#orca_shared.database.use_cases.create_postgres_connection_uri.create_user_uri)
  * [create\_admin\_uri](#orca_shared.database.use_cases.create_postgres_connection_uri.create_admin_uri)
* [orca\_shared.database.use\_cases](#orca_shared.database.use_cases)
* [orca\_shared.database.use\_cases.validation](#orca_shared.database.use_cases.validation)
  * [validate\_postgres\_name](#orca_shared.database.use_cases.validation.validate_postgres_name)
* [orca\_shared.database.entities.postgres\_connection\_info](#orca_shared.database.entities.postgres_connection_info)
* [orca\_shared.database.entities](#orca_shared.database.entities)
* [orca\_shared.recovery.test.unit\_tests.test\_shared\_recovery](#orca_shared.recovery.test.unit_tests.test_shared_recovery)
  * [TestSharedRecoveryLibraries](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries)
    * [setUp](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.setUp)
    * [tearDown](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.tearDown)
    * [test\_post\_entry\_to\_fifo\_queue\_no\_errors](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_post_entry_to_fifo_queue_no_errors)
    * [test\_post\_entry\_to\_standard\_queue\_happy\_path](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_post_entry_to_standard_queue_happy_path)
    * [test\_create\_status\_for\_job\_no\_errors](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_create_status_for_job_no_errors)
    * [test\_update\_status\_for\_file\_no\_errors](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_update_status_for_file_no_errors)
    * [test\_update\_status\_for\_file\_raise\_errors\_error\_message](#orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_update_status_for_file_raise_errors_error_message)
* [orca\_shared.recovery](#orca_shared.recovery)
* [orca\_shared.recovery.shared\_recovery](#orca_shared.recovery.shared_recovery)
  * [RequestMethod](#orca_shared.recovery.shared_recovery.RequestMethod)
  * [OrcaStatus](#orca_shared.recovery.shared_recovery.OrcaStatus)
  * [get\_aws\_region](#orca_shared.recovery.shared_recovery.get_aws_region)
  * [create\_status\_for\_job](#orca_shared.recovery.shared_recovery.create_status_for_job)
  * [update\_status\_for\_file](#orca_shared.recovery.shared_recovery.update_status_for_file)
  * [post\_entry\_to\_fifo\_queue](#orca_shared.recovery.shared_recovery.post_entry_to_fifo_queue)
  * [post\_entry\_to\_standard\_queue](#orca_shared.recovery.shared_recovery.post_entry_to_standard_queue)

<a id="orca_shared"></a>

# orca\_shared

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation"></a>

# orca\_shared.reconciliation.test.unit\_tests.test\_shared\_reconciliation

Name: test_shared_reconciliation.py
Description: Unit tests for shared_reconciliation.py shared library.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries"></a>

## TestSharedReconciliationLibraries Objects

```python
class TestSharedReconciliationLibraries(unittest.TestCase)
```

Unit tests for the shared_reconciliation library used by ORCA Reconciliation Lambdas.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_get_partition_name_from_bucket_name_happy_path"></a>

#### test\_get\_partition\_name\_from\_bucket\_name\_happy\_path

```python
@patch(
    "orca_shared.reconciliation.shared_reconciliation.validate_postgres_name")
def test_get_partition_name_from_bucket_name_happy_path(
        mock_validate_name: MagicMock)
```

Should replace dashes with underscores.
Leave this test hardcoded to avoid unintentional deviations from DB.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_happy_path"></a>

#### test\_update\_job\_happy\_path

```python
@patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
def test_update_job_happy_path(mock_internal_update_job: MagicMock)
```

Happy path for updating job entry with status.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_error_message_required_on_error_status"></a>

#### test\_update\_job\_error\_message\_required\_on\_error\_status

```python
@patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
def test_update_job_error_message_required_on_error_status(
        mock_internal_update_job: MagicMock)
```

Happy path for updating job entry with status.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_update_job_error_message_only_valid_on_error_status"></a>

#### test\_update\_job\_error\_message\_only\_valid\_on\_error\_status

```python
@patch("orca_shared.reconciliation.shared_reconciliation.internal_update_job")
def test_update_job_error_message_only_valid_on_error_status(
        mock_internal_update_job: MagicMock)
```

Error message can only be applied on error statuses. Otherwise, raise an error.

<a id="orca_shared.reconciliation.test.unit_tests.test_shared_reconciliation.TestSharedReconciliationLibraries.test_internal_update_job_error_logged_and_raised"></a>

#### test\_internal\_update\_job\_error\_logged\_and\_raised

```python
@patch("orca_shared.reconciliation.shared_reconciliation.LOGGER")
@patch("orca_shared.reconciliation.shared_reconciliation.update_job_sql")
def test_internal_update_job_error_logged_and_raised(
        mock_update_job_sql: MagicMock, mock_logger: MagicMock)
```

Exceptions from Postgres should bubble up.

<a id="orca_shared.reconciliation"></a>

# orca\_shared.reconciliation

<a id="orca_shared.reconciliation.shared_reconciliation"></a>

# orca\_shared.reconciliation.shared\_reconciliation

Name: shared_reconciliation.py
Description: Shared library that combines common functions and classes needed for
             reconciliation operations.

<a id="orca_shared.reconciliation.shared_reconciliation.OrcaStatus"></a>

## OrcaStatus Objects

```python
class OrcaStatus(Enum)
```

An enumeration.
Defines the status value used in the ORCA Reconciliation database
for use by the reconciliation functions.

<a id="orca_shared.reconciliation.shared_reconciliation.get_partition_name_from_bucket_name"></a>

#### get\_partition\_name\_from\_bucket\_name

```python
def get_partition_name_from_bucket_name(bucket_name: str)
```

Used for interacting with the reconcile_s3_object table.
Provides a valid partition name given an Orca bucket name.
Changes to this function may require a DB migration to recreate partitions.

bucket_name: The name of the Orca bucket in AWS.

<a id="orca_shared.reconciliation.shared_reconciliation.update_job"></a>

#### update\_job

```python
def update_job(job_id: int, status: OrcaStatus, error_message: Optional[str],
               engine: Engine) -> None
```

Updates the status entry for a job.

**Arguments**:

- `job_id` - The id of the job to associate info with.
- `status` - The status to update the job with.
- `error_message` - The error to post to the job, if any.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="orca_shared.reconciliation.shared_reconciliation.internal_update_job"></a>

#### internal\_update\_job

```python
@shared_db.retry_operational_error()
def internal_update_job(job_id: int, status: OrcaStatus, last_update: datetime,
                        end_time: Optional[datetime],
                        error_message: Optional[str], engine: Engine) -> None
```

Updates the status entry for a job.

**Arguments**:

- `job_id` - The id of the job to associate info with.
- `status` - The status to update the job with.
- `last_update` - Datetime returned by datetime.now(timezone.utc)
- `end_time` - Datetime the job ended, if applicable
- `error_message` - The error to post to the job, if any.
- `engine` - The sqlalchemy engine to use for contacting the database.

<a id="orca_shared.database.test.unit_tests.adapters"></a>

# orca\_shared.database.test.unit\_tests.adapters

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws"></a>

# orca\_shared.database.test.unit\_tests.adapters.api.test\_aws

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS"></a>

## TestAWS Objects

```python
class TestAWS(unittest.TestCase)
```

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.setUp"></a>

#### setUp

```python
def setUp()
```

Perform initial setup for test.

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_happy_path"></a>

#### test\_get\_configuration\_happy\_path

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
@patch("orca_shared.database.adapters.api.aws.validate_config")
def test_get_configuration_happy_path(mock_validate_config: MagicMock)
```

Get secret value and return data class.

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_no_aws_region"></a>

#### test\_get\_configuration\_no\_aws\_region

```python
@patch.dict(
    os.environ,
    {},
    clear=True,
)
def test_get_configuration_no_aws_region()
```

Validate an error is thrown if AWS_REGION is not set.

<a id="orca_shared.database.test.unit_tests.adapters.api.test_aws.TestAWS.test_get_configuration_bad_secret"></a>

#### test\_get\_configuration\_bad\_secret

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
def test_get_configuration_bad_secret()
```

Validates a secret is thrown if a secretsmanager ID is invalid.

<a id="orca_shared.database.test.unit_tests.adapters.api"></a>

# orca\_shared.database.test.unit\_tests.adapters.api

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation"></a>

# orca\_shared.database.test.unit\_tests.use\_cases.test\_validation

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri"></a>

## TestCreatePostgresConnectionUri Objects

```python
class TestCreatePostgresConnectionUri(unittest.TestCase)
```

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_config_happy_path"></a>

#### test\_validate\_config\_happy\_path

```python
@patch("orca_shared.database.use_cases.validation._validate_password")
@patch("orca_shared.database.use_cases.validation.validate_postgres_name")
def test_validate_config_happy_path(mock_validate_postgres_name: MagicMock,
                                    mock_validate_password: MagicMock)
```

Should call proper validation functions for various properties.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_happy_path"></a>

#### test\_validate\_password\_happy\_path

```python
def test_validate_password_happy_path()
```

A password must have lower case and upper case letters,
a number between 0 and 9, a special character and
length of 12.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_short_raises_error"></a>

#### test\_validate\_password\_short\_raises\_error

```python
def test_validate_password_short_raises_error()
```

A password of `None` or length < 12 should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_number_missing_raises_error"></a>

#### test\_validate\_password\_number\_missing\_raises\_error

```python
def test_validate_password_number_missing_raises_error()
```

A password without a number should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_upper_case_missing_raises_error"></a>

#### test\_validate\_password\_upper\_case\_missing\_raises\_error

```python
def test_validate_password_upper_case_missing_raises_error()
```

A password without an upper case letter should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_lower_case_missing_raises_error"></a>

#### test\_validate\_password\_lower\_case\_missing\_raises\_error

```python
def test_validate_password_lower_case_missing_raises_error()
```

A password without a lower case letter should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_password_special_character_missing_raises_error"></a>

#### test\_validate\_password\_special\_character\_missing\_raises\_error

```python
def test_validate_password_special_character_missing_raises_error()
```

A password without a special character should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_happy_path"></a>

#### test\_validate\_postgres\_name\_happy\_path

```python
def test_validate_postgres_name_happy_path()
```

A name of any length starting with a letter should be accepted.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_short_raises_error"></a>

#### test\_validate\_postgres\_name\_short\_raises\_error

```python
def test_validate_postgres_name_short_raises_error()
```

A name of `None` or length < 1 should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_long_raises_error"></a>

#### test\_validate\_postgres\_name\_long\_raises\_error

```python
def test_validate_postgres_name_long_raises_error()
```

A name of length > 63 should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases.test_validation.TestCreatePostgresConnectionUri.test_validate_postgres_name_invalid_raises_error"></a>

#### test\_validate\_postgres\_name\_invalid\_raises\_error

```python
def test_validate_postgres_name_invalid_raises_error()
```

A name starting with a non-letter or containing illegal characters should be rejected.

<a id="orca_shared.database.test.unit_tests.use_cases"></a>

# orca\_shared.database.test.unit\_tests.use\_cases

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri"></a>

# orca\_shared.database.test.unit\_tests.use\_cases.test\_create\_postgres\_connection\_uri

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri"></a>

## TestCreatePostgresConnectionUri Objects

```python
class TestCreatePostgresConnectionUri(unittest.TestCase)
```

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_user_uri_happy_path"></a>

#### test\_create\_user\_uri\_happy\_path

```python
@patch(
    "orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri"
)
def test_create_user_uri_happy_path(mock_create_connection_uri: MagicMock)
```

With no optional properties, return admin database uri.

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_admin_uri_happy_path"></a>

#### test\_create\_admin\_uri\_happy\_path

```python
@patch(
    "orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri"
)
def test_create_admin_uri_happy_path(mock_create_connection_uri: MagicMock)
```

With no optional properties, return admin database uri.

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test_create_admin_uri_overwrite_database"></a>

#### test\_create\_admin\_uri\_overwrite\_database

```python
@patch(
    "orca_shared.database.use_cases.create_postgres_connection_uri._create_connection_uri"
)
def test_create_admin_uri_overwrite_database(
        mock_create_connection_uri: MagicMock)
```

If database name parameter added, use it.

<a id="orca_shared.database.test.unit_tests.use_cases.test_create_postgres_connection_uri.TestCreatePostgresConnectionUri.test__create_connection_uri_happy_path"></a>

#### test\_\_create\_connection\_uri\_happy\_path

```python
def test__create_connection_uri_happy_path()
```

Basic happy path.

<a id="orca_shared.database.test.unit_tests.test_shared_db"></a>

# orca\_shared.database.test.unit\_tests.test\_shared\_db

Name: test_shared_db.py

Description: Runs unit tests for the shared_db.py library.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries"></a>

## TestSharedDatabaseLibraries Objects

```python
class TestSharedDatabaseLibraries(unittest.TestCase)
```

Runs unit tests for all of the functions in the shared_db library.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.setUp"></a>

#### setUp

```python
def setUp()
```

Perform initial setup for test.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.tearDown"></a>

#### tearDown

```python
def tearDown()
```

Perform tear down actions

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_happy_path"></a>

#### test\_get\_configuration\_happy\_path

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
def test_get_configuration_happy_path()
```

Testing the rainbows and bunnies path of this call.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_no_aws_region"></a>

#### test\_get\_configuration\_no\_aws\_region

```python
@patch.dict(
    os.environ,
    {},
    clear=True,
)
def test_get_configuration_no_aws_region()
```

Validate an error is thrown if AWS_REGION is not set.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_configuration_bad_secret"></a>

#### test\_get\_configuration\_bad\_secret

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
def test_get_configuration_bad_secret()
```

Validates a secret is thrown if a secretsmanager ID is invalid.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_admin_connection_database_values"></a>

#### test\_get\_admin\_connection\_database\_values

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
@patch("orca_shared.database.shared_db._create_connection")
def test_get_admin_connection_database_values(mock_connection: MagicMock)
```

Tests the function to make sure the correct database value is passed.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_get_user_connection_database_values"></a>

#### test\_get\_user\_connection\_database\_values

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
@patch("orca_shared.database.shared_db._create_connection")
def test_get_user_connection_database_values(mock_connection: MagicMock)
```

Tests the function to make sure the correct database value is passed.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test__create_connection_call_values"></a>

#### test\_\_create\_connection\_call\_values

```python
@patch.dict(
    os.environ,
    {
        "AWS_REGION": "us-west-2",
    },
    clear=True,
)
@patch("orca_shared.database.shared_db.create_engine")
def test__create_connection_call_values(mock_connection: MagicMock)
```

Tests the function to make sure the correct database value is passed.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_retry_operational_error_non_operational_error_raises"></a>

#### test\_retry\_operational\_error\_non\_operational\_error\_raises

```python
@patch("time.sleep")
def test_retry_operational_error_non_operational_error_raises(
        mock_sleep: MagicMock)
```

If the error raised is not an OperationalError, it should just be raised.

<a id="orca_shared.database.test.unit_tests.test_shared_db.TestSharedDatabaseLibraries.test_retry_operational_error_operational_error_retries_and_raises"></a>

#### test\_retry\_operational\_error\_operational\_error\_retries\_and\_raises

```python
@patch("time.sleep")
def test_retry_operational_error_operational_error_retries_and_raises(
        mock_sleep: MagicMock)
```

If the error raised is an OperationalError, it should retry up to the maximum allowed.

<a id="orca_shared.database.shared_db"></a>

# orca\_shared.database.shared\_db

Name: shared_db.py

Description: Shared library for database objects needed by the various libraries.

<a id="orca_shared.database.shared_db.get_configuration"></a>

#### get\_configuration

```python
def get_configuration(db_connect_info_secret_arn: str) -> Dict[str, str]
```

Create a dictionary of configuration values based on environment variables
and secret information items needed to create ORCA database connections.


```
Environment Variables:
    AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.
```

**Arguments**:

- `db_connect_info_secret_arn` _str_ - The secret ARN of the secret in AWS secretsmanager.
  

**Returns**:

- `Configuration` _Dict_ - Dictionary with all of the configuration information.
  The schema for the output is available [here](schemas/output.json).
  

**Raises**:

- `Exception` _Exception_ - When variables or secrets are not available.

<a id="orca_shared.database.shared_db.get_admin_connection"></a>

#### get\_admin\_connection

```python
def get_admin_connection(config: Dict[str, str],
                         database: str = None) -> Engine
```

Creates a connection engine to a database as a superuser.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
- `database` _str_ - Database for the admin user to connect to. Defaults to admin_database.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

<a id="orca_shared.database.shared_db.get_user_connection"></a>

#### get\_user\_connection

```python
def get_user_connection(config: Dict[str, str]) -> Engine
```

Creates a connection engine to the application database as the application
database user.

**Arguments**:

- `config` _Dict_ - Configuration containing connection information.
  
  Returns
- `Engine` _sqlalchemy.future.Engine_ - engine object for creating database connections.

<a id="orca_shared.database.shared_db.retry_operational_error"></a>

#### retry\_operational\_error

```python
def retry_operational_error(
    max_retries: int = MAX_RETRIES,
    backoff_in_seconds: int = INITIAL_BACKOFF_IN_SECONDS,
    backoff_factor: int = BACKOFF_FACTOR
) -> Callable[[Callable[[], RT]], Callable[[], RT]]
```

Decorator takes arguments to adjust number of retries and backoff strategy.

**Arguments**:

- `max_retries` _int_ - number of times to retry in case of failure.
- `backoff_in_seconds` _int_ - Number of seconds to sleep the first time through.
- `backoff_factor` _int_ - Value of the factor used for backoff.

<a id="orca_shared.database"></a>

# orca\_shared.database

<a id="orca_shared.database.adapters"></a>

# orca\_shared.database.adapters

<a id="orca_shared.database.adapters.api"></a>

# orca\_shared.database.adapters.api

<a id="orca_shared.database.adapters.api.aws"></a>

# orca\_shared.database.adapters.api.aws

<a id="orca_shared.database.adapters.api.aws.get_configuration"></a>

#### get\_configuration

```python
def get_configuration(db_connect_info_secret_arn: str,
                      logger: logging.Logger) -> PostgresConnectionInfo
```

Create a dictionary of configuration values based on environment variables
and secret information items needed to create ORCA database connections.


```
Environment Variables:
    AWS_REGION (str): AWS reserved runtime variable used to set boto3 client region.
```

**Arguments**:

- `db_connect_info_secret_arn` - The secret ARN of the secret in AWS secretsmanager.
- `logger` - The logger to use.
  

**Returns**:

- `Configuration` _Dict_ - Dictionary with all the configuration information.
  The schema for the output is available [here](schemas/output.json).
  

**Raises**:

- `Exception` - When variables or secrets are not available,
  or if configured values are illegal.

<a id="orca_shared.database.use_cases.create_postgres_connection_uri"></a>

# orca\_shared.database.use\_cases.create\_postgres\_connection\_uri

<a id="orca_shared.database.use_cases.create_postgres_connection_uri.create_user_uri"></a>

#### create\_user\_uri

```python
def create_user_uri(db_connect_info: PostgresConnectionInfo,
                    logger: logging.Logger) -> str
```

Creates a connection URI for application database as the application
database user.

**Arguments**:

- `db_connect_info` - Configuration containing connection information.
- `logger` - The logger to use.
  

**Returns**:

  URI for connecting to the database.

<a id="orca_shared.database.use_cases.create_postgres_connection_uri.create_admin_uri"></a>

#### create\_admin\_uri

```python
def create_admin_uri(db_connect_info: PostgresConnectionInfo,
                     logger: logging.Logger,
                     database_name_overwrite: str = None) -> str
```

Creates a connection URI for a database as a superuser.

**Arguments**:

- `db_connect_info` - Configuration containing connection information.
- `logger` - The logger to use.
- `database_name_overwrite` - Database to connect to. Defaults to admin_database.
  

**Returns**:

  URI for connecting to the database.

<a id="orca_shared.database.use_cases"></a>

# orca\_shared.database.use\_cases

<a id="orca_shared.database.use_cases.validation"></a>

# orca\_shared.database.use\_cases.validation

<a id="orca_shared.database.use_cases.validation.validate_postgres_name"></a>

#### validate\_postgres\_name

```python
def validate_postgres_name(name: str, context: str,
                           logger: logging.Logger) -> None
```

Validates the given name against documented Postgres restrictions.
https://www.postgresql.org/docs/14/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS

**Raises**:

- `Exception` - If value is empty, is more than 63 characters, or contains illegal characters.

<a id="orca_shared.database.entities.postgres_connection_info"></a>

# orca\_shared.database.entities.postgres\_connection\_info

<a id="orca_shared.database.entities"></a>

# orca\_shared.database.entities

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery"></a>

# orca\_shared.recovery.test.unit\_tests.test\_shared\_recovery

Name: test_shared_recovery.py
Description: Unit tests for shared_recovery.py shared library.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries"></a>

## TestSharedRecoveryLibraries Objects

```python
class TestSharedRecoveryLibraries(unittest.TestCase)
```

Unit tests for the shared_recovery library used by ORCA Recovery Lambdas.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.setUp"></a>

#### setUp

```python
def setUp()
```

Perform initial setup for the tests.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.tearDown"></a>

#### tearDown

```python
def tearDown()
```

Perform teardown for the tests

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_post_entry_to_fifo_queue_no_errors"></a>

#### test\_post\_entry\_to\_fifo\_queue\_no\_errors

```python
@patch.dict(
    os.environ,
    {"AWS_REGION": "us-west-2"},
    clear=True,
)
def test_post_entry_to_fifo_queue_no_errors()
```

*Happy Path*
Test that sending a message to SQS queue using post_entry_to_fifo_queue()
function returns the same expected message.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_post_entry_to_standard_queue_happy_path"></a>

#### test\_post\_entry\_to\_standard\_queue\_happy\_path

```python
@patch.dict(
    os.environ,
    {"AWS_REGION": "us-west-2"},
    clear=True,
)
def test_post_entry_to_standard_queue_happy_path()
```

*Happy Path*
Test that sending a message to SQS queue using post_entry_to_standard_queue()
function returns the same expected message.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_create_status_for_job_no_errors"></a>

#### test\_create\_status\_for\_job\_no\_errors

```python
@patch.dict(
    os.environ,
    {"AWS_REGION": "us-west-2"},
    clear=True,
)
def test_create_status_for_job_no_errors()
```

*Happy Path*
Tests that messages are correctly constructed by function and sent to
the queue based on RequestMethod and Status values.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_update_status_for_file_no_errors"></a>

#### test\_update\_status\_for\_file\_no\_errors

```python
@patch.dict(
    os.environ,
    {"AWS_REGION": "us-west-2"},
    clear=True,
)
def test_update_status_for_file_no_errors()
```

*Happy Path*
Test that sending a message to SQS queue using post_status_for_file
function returns the same expected message.

<a id="orca_shared.recovery.test.unit_tests.test_shared_recovery.TestSharedRecoveryLibraries.test_update_status_for_file_raise_errors_error_message"></a>

#### test\_update\_status\_for\_file\_raise\_errors\_error\_message

```python
def test_update_status_for_file_raise_errors_error_message()
```

Tests that update_status_for_file will raise a ValueError
if the error_message is either empty or None in case of status_id as FAILED.
request_method is set as NEW since the logics only apply for it.

<a id="orca_shared.recovery"></a>

# orca\_shared.recovery

<a id="orca_shared.recovery.shared_recovery"></a>

# orca\_shared.recovery.shared\_recovery

Name: shared_recovery.py
Description: Shared library that combines common functions and classes needed for
             recovery operations.

<a id="orca_shared.recovery.shared_recovery.RequestMethod"></a>

## RequestMethod Objects

```python
class RequestMethod(Enum)
```

An enumeration.
Provides potential actions for the database lambda to take when posting to the SQS queue.

<a id="orca_shared.recovery.shared_recovery.OrcaStatus"></a>

## OrcaStatus Objects

```python
class OrcaStatus(Enum)
```

An enumeration.
Defines the status value used in the ORCA Recovery database for use by the recovery functions.

<a id="orca_shared.recovery.shared_recovery.get_aws_region"></a>

#### get\_aws\_region

```python
def get_aws_region() -> str
```

Gets AWS region variable from the runtime environment variable.

**Returns**:

  The AWS region variable.

**Raises**:

- `Exception` - Thrown if AWS region is empty or None.

<a id="orca_shared.recovery.shared_recovery.create_status_for_job"></a>

#### create\_status\_for\_job

```python
def create_status_for_job(job_id: str, granule_id: str,
                          archive_destination: str,
                          files: List[Dict[str, Any]], db_queue_url: str)
```

Creates status information for a new job and its files, and posts to queue.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `archive_destination` - The S3 bucket destination of where the data is archived.
- `files` - A List of Dicts with the following keys:
  'filename' (str)
  'keyPath' (str)
  'restoreDestination' (str)
  's3MultipartChunksizeMb' (int)
  'statusId' (int)
  'errorMessage' (str, Optional)
  'requestTime' (str)
  'lastUpdate' (str)
  'completionTime' (str, Optional)
- `db_queue_url` - The SQS queue URL defined by AWS.

<a id="orca_shared.recovery.shared_recovery.update_status_for_file"></a>

#### update\_status\_for\_file

```python
def update_status_for_file(job_id: str, granule_id: str, filename: str,
                           orca_status: OrcaStatus,
                           error_message: Optional[str], db_queue_url: str)
```

Creates update information for a file's status entry, and posts to queue.
Queue entry will be rejected by post_to_database if status for
job_id + granule_id + filename does not exist.

**Arguments**:

- `job_id` - The unique identifier used for tracking requests.
- `granule_id` - The id of the granule being restored.
- `filename` - The name of the file being copied.
- `orca_status` - Defines the status id used in the ORCA Recovery database.
- `error_message` - message displayed on error.
- `db_queue_url` - The SQS queue URL defined by AWS.

<a id="orca_shared.recovery.shared_recovery.post_entry_to_fifo_queue"></a>

#### post\_entry\_to\_fifo\_queue

```python
def post_entry_to_fifo_queue(new_data: Dict[str, Any],
                             request_method: RequestMethod,
                             db_queue_url: str) -> None
```

Posts messages to SQS FIFO queue.

**Arguments**:

- `new_data` - A dictionary representing the column/value pairs to write to the DB table.
- `request_method` - The action for the database lambda to take when posting to the SQS queue.
- `db_queue_url` - The SQS queue URL defined by AWS.

**Raises**:

  None

<a id="orca_shared.recovery.shared_recovery.post_entry_to_standard_queue"></a>

#### post\_entry\_to\_standard\_queue

```python
def post_entry_to_standard_queue(new_data: Dict[str, Any],
                                 recovery_queue_url: str) -> None
```

Posts messages to the recovery standard SQS queue.

**Arguments**:

- `new_data` - A dictionary representing the column/value pairs to write to the DB table.
- `recovery_queue_url` - The SQS queue URL defined by AWS.

**Raises**:

  None

