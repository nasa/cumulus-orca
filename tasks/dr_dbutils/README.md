[![Known Vulnerabilities](https://snyk.io/test/github/nasa/cumulus-orca/badge.svg?targetFile=tasks/dr_dbutils/requirements.txt)](https://snyk.io/test/github/nasa/cumulus-orca?targetFile=tasks/dr_dbutils/requirements.txt)

Visit the [Developer Guide](https://nasa.github.io/cumulus-orca/docs/developer/development-guide/code/contrib-code-intro) for information on environment setup and testing.

**Lambda function request_files**

- [Deployment](#deployment)
- [pydoc requests_db](#pydoc-requests-db)

<a name="development"></a>
# Development

## Deployment
```
https://www.oreilly.com/library/view/head-first-python/9781491919521/ch04.html
Create the distribution file:
    (podr) λ cd C:\devpy\poswotdr\tasks\dr_dbutils
    (podr) λ py -3 setup.py sdist
    (podr) λ cd dist
    (podr) λ pip install dr_dbutils-1.0.tar.gz

```
<a name="pydoc-requests-db"></a>
## pydoc requests_db
```
NAME
    requests_db

DESCRIPTION
    This module exists to keep all database specific code for the request_status
    table in a single place.

CLASSES
    builtins.Exception(builtins.BaseException)
        BadRequestError
        DatabaseError
        NotFound
    
    class BadRequestError(builtins.Exception)
     |  Exception to be raised if there is a problem with the request.
     |  
     |  Method resolution order:
     |      BadRequestError
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
    
    class DatabaseError(builtins.Exception)
     |  Exception to be raised when there's a database error.
     |  
     |  Method resolution order:
     |      DatabaseError
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
    
    class NotFound(builtins.Exception)
     |  Exception to be raised when a request doesn't exist.
     |  
     |  Method resolution order:
     |      NotFound
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
    create_data(obj, job_type=None, job_status=None, request_time=None, last_update_time=None, err_msg=None)
        Creates a dict containing the input data for submit_request.
    
    datetime_to_string_converter(obj: <built-in function any>) -> Union[str, NoneType]
        # todo: Why is this the default?
    
    delete_all_requests()
        Deletes everything from the request_status table.
        
        TODO: Currently this method is only used to facilitate testing,
        so unit tests may not be complete.
    
    delete_request(request_id)
        Deletes a job by request_id.
    
    get_all_requests()
        Returns all of the requests.
    
    get_dbconnect_info()
        Gets the dbconnection info. PREFIX environment variable expected to be set.
    
    get_job_by_request_id(request_id)
        Reads a row from request_status by request_id.
    
    get_jobs_by_granule_id(granule_id)
        Reads rows from request_status by granule_id.
    
    get_jobs_by_object_key(object_key)
        Reads rows from request_status by object_key.
    
    get_jobs_by_request_group_id(request_group_id)
        Returns rows from request_status for a request_group_id
    
    get_jobs_by_status(status, max_days_old=None)
        Returns rows from request_status by status, and optional days old
    
    get_utc_now_iso()
        Returns the current utc timestamp as a string in isoformat
        ex. '2019-07-17T17:36:38.494918'
    
    request_id_generator()
        Returns a request_group_id (UUID) to be used to identify all the files for a granule
        ex. '0000a0a0-a000-00a0-00a0-0000a0000000'
    
    result_to_json(result_rows: list) -> list
        Converts a database result to Json format
        
        Args:
            result_rows: The object to convert to json.
        
        Returns: todo
    
    submit_request(data)
        Takes the provided request data (as a dict) and attempts to update the
        database with a new request.
        
        Raises BadRequestError if there is a problem with the input.
    
    update_request_status_for_job(request_id, status, err_msg=None)
        Updates the status of a job.

DATA
    LOGGER = <Logger requests_db (WARNING)>
    Optional = typing.Optional
```