[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_from_archive/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_from_archive/requirements.txt)

**Lambda function copy_from_archive**

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Deployment](#deployment)
  * [Deployment Validation](#deployment-validation)
- [pydoc copy_from_archive](#pydoc-copy-files)

<a name="deployment"></a>
## Deployment
```
    see bin/build_tasks.sh to build the zip file. Upload the zip file to AWS.
```
<a name="deployment-validation"></a>
### Deployment Validation
```
1.  Paste the contents of test/testevents/copy_exp_event_1.json into
    a test event and execute it.
2.  Neither the source_key or the source_bucket should exist, so the copy will fail
    and the database update will fail.

```
<a name="pydoc-copy-files"></a>
## pydoc copy_from_archive
[See the API documentation for more details.](API.md)