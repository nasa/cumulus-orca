[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/orca_catalog_reporting_dummy/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/orca_catalog_reporting_dummy/requirements.txt)

**Lambda function orca_catalog_reporting_dummy **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc orca_catalog_reporting_dummy](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "providerId": ["lpdaac"],
  "collectionId": ["MOD14A1__061"],
  "granuleId": ["MOD14A1.061.A23V45.2020235"],
  "startTimestamp": "2020-01-01T23:00:00+00:00",
  "endTimestamp": "2020-01-02T23:00:00+00:00"
}
```

### Example Output
```json
[
  {
    "providerId": "lpdaac",
    "collections": [
      {
        "collectionId": "MOD14A1__061",
        "granules": [
          {
            "granuleId": "MOD14A1.061.A23V45.2020235",
            "date": "TBD",
            "createDate": "2020-01-01T23:00:00+0",
            "lastUpdate": "2020-01-01T23:00:00+0",
            "files": [
              {
                "fileName": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
                "orcaLocation": "s3://orca-archive/MOD14A1/061/...",
                "fileSize": 100934568723,
                "fileChecksum": "ACFH325128030192834127347",
                "fileChecksumType": "SHA-256",
                "fileVersion": "VXCDEG902",
                "orcaEtag": "YXC432BGT789"
              },
              ...
            ]
          },
          ...
        ]
      },
      ...
    ]
  },
  ...
]
```
<a name="pydoc"></a>
## pydoc orca_catalog_reporting_dummy
```
Help on module orca_catalog_reporting_dummy:

NAME
    orca_catalog_reporting_dummy

FUNCTIONS
    create_http_error_dict(error_type: str, http_status_code: int, request_id: str, message: str) -> Dict[str, Any]
        Creates a standardized dictionary for error reporting.
        Args:
            error_type: The string representation of http_status_code.
            http_status_code: The integer representation of the http error.
            request_id: The incoming request's id.
            message: The message to display to the user and to record for debugging.
        Returns:
            A dict with the following keys:
                'errorType' (str)
                'httpStatus' (int)
                'requestId' (str)
                'message' (str)
    
    handler(event: Dict[str, Any], context: Any) -> List[Dict[str, Any]]
        Entry point for the orca_catalog_reporting_dummy Lambda.
        Args:
            event: See schemas/input.json
            context: An object provided by AWS Lambda. Used for context tracking.
        
        Returns: 
            See schemas/output.json
            Or, if an error occurs, see create_http_error_dict

DATA
    Any = typing.Any
    Dict = typing.Dict
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
```