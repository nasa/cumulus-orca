[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/orca_catalog_reporting/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/orca_catalog_reporting/requirements.txt)

**Lambda function orca_catalog_reporting**

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc orca_catalog_reporting](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  "pageIndex": 0,
  "providerId": ["lpdaac"],
  "collectionId": ["MOD14A1__061"],
  "granuleId": ["MOD14A1.061.A23V45.2020235"],
  "startTimestamp": "628021800000",
  "endTimestamp": "628021900000"
}
```

### Example Output
```json
{
  "anotherPage": false,
  "granules": [
    {
      "providerId": "lpdaac",
      "collectionId": "MOD14A1___061",
      "id": "MOD14A1.061.A23V45.2020235",
      "createdAt": "628021850000",
      "executionId": "u654-123-Yx679",
      "ingestDate": "628021950000",
      "lastUpdate": "628021970000",
      "files": [
        {
          "name": "MOD14A1.061.A23V45.2020235.2020240145621.hdf",
          "cumulusArchiveLocation": "cumulus-bucket",
          "orcaArchiveLocation": "orca-archive",
          "keyPath": "MOD14A1/061/032/MOD14A1.061.A23V45.2020235.2020240145621.hdf",
          "sizeBytes": 100934568723,
          "hash": "ACFH325128030192834127347",
          "hashType": "SHA-256",
          "storageClass": "GLACIER",
          "version": "VXCDEG902"
        }
      ]
    }
  ]
}
```
<a name="pydoc"></a>
## pydoc orca_catalog_reporting
[See the API documentation for more details.](API.md)