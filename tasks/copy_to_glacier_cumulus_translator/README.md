[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/copy_to_glacier_cumulus_translator/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/copy_to_glacier_cumulus_translator/requirements.txt)

**Lambda function copy_to_glacier_cumulus_translator **

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

- [Input/Output Schemas and Examples](#input-output-schemas)
- [pydoc copy_to_glacier_cumulus_translator](#pydoc)

<a name="input-output-schemas"></a>
## Input/Output Schemas and Examples
Fully defined json schemas written in the schema of https://json-schema.org/ can be found in the [schemas folder](schemas).

### Example Input
```json
{
  todo
}
```

### Example Output
```json
{
  todo
}
```
<a name="pydoc"></a>
## pydoc copy_to_glacier_cumulus_translator
```
Help on module copy_to_glacier_cumulus_translator:

NAME
    copy_to_glacier_cumulus_translator

CLASSES
    builtins.Exception(builtins.BaseException)
        ReformatRequestError
    
    class ReformatRequestError(builtins.Exception)
     |  Exception to be raised if the request fails in any way.
     |  
     |  Method resolution order:
     |      ReformatRequestError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |  
     |  Data descriptors defined here:
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.Exception:
     |  
     |  __init__(self, /, *args, **kwargs)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |  
     |  __new__(*args, **kwargs) from builtins.type
     |      Create and return a new object.  See help(type) for accurate signature.
     |  
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |  
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |  
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |  
     |  __reduce__(...)
     |      Helper for pickle.
     |  
     |  __repr__(self, /)
     |      Return repr(self).
     |  
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |  
     |  __setstate__(...)
     |  
     |  __str__(self, /)
     |      Return str(self).
     |  
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |  
     |  __cause__
     |      exception cause
     |  
     |  __context__
     |      exception context
     |  
     |  __dict__
     |  
     |  __suppress_context__
     |  
     |  __traceback__
     |  
     |  args

FUNCTIONS
    handler(event: Dict[str, Any], context: Any) -> List[Dict[str, Any]]
        Entry point for the copy_to_glacier_cumulus_translator Lambda.
        Args:
            event: See schemas/input.json, schemas/config.json, and CMA.
            context: An object provided by AWS Lambda. Used for context tracking.
        
        Returns: See schemas/output.json
    
    task(event: Dict[str, Any], context) -> List[Dict[str, Any]]
        Transforms event from Cumulus format to Orca copy_to_glacier format.
        Args:
            event: A dict with the following keys:
                'input': See schemas/input.json
                'config': See schemas/config.json
            context: An object passed through by CMA. Unused.
        
        Returns:
            See schemas/output.json

DATA
    Any = typing.Any
    Dict = typing.Dict
    LOGGER = <cumulus_logger.CumulusLogger object>
    List = typing.List
```