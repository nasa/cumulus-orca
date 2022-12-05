# Table of Contents

* [extract\_filepaths\_for\_granule](#extract_filepaths_for_granule)
  * [ExtractFilePathsError](#extract_filepaths_for_granule.ExtractFilePathsError)
  * [task](#extract_filepaths_for_granule.task)
  * [get\_regex\_buckets](#extract_filepaths_for_granule.get_regex_buckets)
  * [should\_exclude\_files\_type](#extract_filepaths_for_granule.should_exclude_files_type)
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
def task(event)
```

Task called by the handler to perform the work.

This task will parse the input, removing the granuleId and file keys for a granule.

**Arguments**:

- `event` _dict_ - passed through from the handler
  

**Returns**:

- `dict` - dict containing granuleId and keys. See handler for detail.
  

**Raises**:

- `ExtractFilePathsError` - An error occurred parsing the input.

<a id="extract_filepaths_for_granule.get_regex_buckets"></a>

#### get\_regex\_buckets

```python
def get_regex_buckets(event) -> Dict[str, str]
```

Gets a dict of regular expressions and the corresponding archive bucket for files
matching the regex.

**Arguments**:

- `event` _dict_ - passed through from the handler
  

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

Tests whether or not file is included in {excludedFileExtensions} from copy_to_archive.

**Arguments**:

- `file_key` - The key of the file within the s3 bucket.
- `exclude_file_types` - List of extensions to exclude in the backup.

**Returns**:

  True if file should be excluded from copy, False otherwise.

<a id="extract_filepaths_for_granule.handler"></a>

#### handler

```python
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Union[str, int]], context: LambdaContext)
```

Lambda handler. Extracts the key's for a granule from an input dict.

**Arguments**:

- `event` _dict_ - A dict with the following keys:
  
  granules (list(dict)): A list of dict with the following keys:
- `granuleId` _string_ - The id of a granule.
  files (list(dict)): list of dict with the following keys:
- `key` _string_ - The key of the file to be returned.
  other dictionary keys may be included, but are not used.
  other dictionary keys may be included, but are not used.
  
- `Example` - {
                "event": {
                  "granules": [
                    {
                      "granuleId": "granxyz",
                      "recoveryBucketOverride": "test-recovery-bucket",
                      "version": "006",
                      "files": [
                        {
                          "fileName": "file1",
                          "key": "key1",
                          "source": "s3://dr-test-sandbox-protected/file1",
                          "type": "metadata"
                        }
                      ]
                    }
                  ]
                }
              }
  
- `context` - This object provides information about the lambda invocation, function,
  and execution env.
  

**Returns**:

- `dict` - A dict with the following keys:
  
  'granules' (list(dict)): list of dict with the following keys:
- `'granuleId'` _string_ - The id of a granule.
  'keys' (list(string)): list of keys for the granule.
  

**Example**:

- `{"granules"` - [{"granuleId": "granxyz",
- `"keys"` - ["key1",
  "key2"]}]}
  

**Raises**:

- `ExtractFilePathsError` - An error occurred parsing the input.

