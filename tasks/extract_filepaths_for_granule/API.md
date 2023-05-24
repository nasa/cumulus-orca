# Table of Contents

* [extract\_filepaths\_for\_granule](#extract_filepaths_for_granule)
  * [ExtractFilePathsError](#extract_filepaths_for_granule.ExtractFilePathsError)
  * [task](#extract_filepaths_for_granule.task)
  * [get\_regex\_buckets](#extract_filepaths_for_granule.get_regex_buckets)
  * [should\_exclude\_files\_type](#extract_filepaths_for_granule.should_exclude_files_type)
  * [set\_optional\_event\_property](#extract_filepaths_for_granule.set_optional_event_property)
  * [handler](#extract_filepaths_for_granule.handler)

<a id="extract_filepaths_for_granule"></a>

# extract\_filepaths\_for\_granule

Name: extract_filepaths_for_granule.py

Description:  Extracts the keys (filepaths) for a granule's files from a Cumulus Message.

<a id="extract_filepaths_for_granule.ExtractFilePathsError"></a>

## ExtractFilePathsError Objects

```python
class ExtractFilePathsError(Exception)
```

Exception to be raised if any errors occur

<a id="extract_filepaths_for_granule.task"></a>

#### task

```python
def task(task_input: Dict[str, Any], config: Dict[str, Any])
```

Task called by the handler to perform the work.

This task will parse the input, extracting the properties for a granule.

**Arguments**:

- `task_input` - See schemas/input.json
- `config` - See schemas/config.json
  

**Returns**:

- `dict` - dict containing properties for granules. See handler for detail.
  

**Raises**:

- `ExtractFilePathsError` - An error occurred parsing the input.

<a id="extract_filepaths_for_granule.get_regex_buckets"></a>

#### get\_regex\_buckets

```python
def get_regex_buckets(config: Dict[str, Any]) -> Dict[str, str]
```

Gets a dict of regular expressions and the corresponding archive bucket for files
matching the regex.

**Arguments**:

- `config` - See schemas/config.json
  

**Returns**:

- `dict` - dict containing regex and bucket.
  

**Raises**:

- `ExtractFilePathsError` - An error occurred parsing the input.

<a id="extract_filepaths_for_granule.should_exclude_files_type"></a>

#### should\_exclude\_files\_type

```python
def should_exclude_files_type(file_key: str,
                              exclude_file_types: List[str]) -> bool
```

Tests whether file is included in {excludedFileExtensions} from copy_to_archive.

**Arguments**:

- `file_key` - The key of the file within the s3 bucket.
- `exclude_file_types` - List of extensions to exclude in the backup.

**Returns**:

  True if file should be excluded from copy, False otherwise.

<a id="extract_filepaths_for_granule.set_optional_event_property"></a>

#### set\_optional\_event\_property

```python
def set_optional_event_property(event: Dict[str,
                                            Any], target_path_cursor: Dict,
                                target_path_segments: List) -> None
```

Sets the optional variable value from event if present, otherwise sets to None.

**Arguments**:

- `event` - See schemas/input.json.
- `target_path_cursor` - Cursor of the current section to check.
- `target_path_segments` - The path to the current cursor.

**Returns**:

  None

<a id="extract_filepaths_for_granule.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Dict[str, Any]], context: LambdaContext)
```

Lambda handler. Extracts the key's for a granule from an input dict.

**Arguments**:

- `event` - Event passed into the step from the aws workflow.
  See schemas/input.json and schemas/config.json for more information.
  
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  

**Returns**:

  See schemas/output.json for more information.
  

**Raises**:

- `ExtractFilePathsError` - An error occurred parsing the input.

