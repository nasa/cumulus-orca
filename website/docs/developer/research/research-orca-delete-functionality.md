---
id: research-orca-delete-functionality
title: Research Notes on ORCA delete functionality.
description: Research Notes on implementing delete functionality for ORCA.
---

## Delete functionality use cases

Some use cases for delete functionality are as follows:

- As a DAAC, I would like remove data from ORCA that is invalid or expired in order to maintain a clean data archive.

- As a DAAC, I would like to remove data from ORCA only if it has been in glacier for more than 90 days from initial ingest to keep from incurring additional cost for early removal.

    This can be implemented by using soft delete. We can either flag the data in the database with a new column named `Pending Deletion` or we can create a separate table that contains those data marked for deletion. Then after 90 days, we can permanently delete from the DB as well as the glacier bucket.


- As a DAAC, I would like to configure the amount of time data remains in ORCA after being signaled to be deleted.	

    This should be configurable by each DAAC that is using ORCA. Even after the data is deleted from Cumulus, it should stay in ORCA for x number of days for safety reasons.


- As a DAAC, I would like only authorized personnel to be able to remove data from ORCA in a controlled way to minimize risk of accidental or malicious deletions.

    This could be implemented with the use of NASA launchpad authentication. This [link](https://idmax.nasa.gov/nams/asset/255115) is used to submit a new GSFC workflow request and most probably will be used to only allow specific users to perform the deletes. Contact `robert.a.meredith@nasa.gov` and `tadd.buffington@nasa.gov` with any issues regarding launchpad integration.

- As a DAAC, I would like duplicate data to be versioned in ORCA in order to recover the proper version of the data based on the type of failure.	


- Perform a check with CMR and/or Cumulus to verify that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA.

    
    This can be implemented in the existing lambda function that will be used to delete the data from ORCA.

### API gateway

API gateway is currently used by end users for creating reconciliation reports and getting status update of recovery granules and jobs. This can be used for creating API calls made by end users for deletion. The API gateway should act as a trigger to the lambda functions that actually perform the deletion in the backend. An API gateway with two different resources need to be created- one for the soft delete API call and one for the hard delete API call.
Check API gateway [examples](https://github.com/nasa/cumulus-orca/tree/develop/modules/api-gateway) currently used by ORCA. 

### Lambda function

The delete functionality can be performed by two lambda functions based on initial research. One of the lambda functions will be used to perform soft delete- delete from S3 bucket but only flag the granule in the database for deletion after 90 days. The lambda should also verify with CMR and/or Cumulus that the granule has been deleted from those locations prior to allowing the delete to proceed in ORCA. The lambda will be triggered by an API call made by the user once the user is authenticated with Launchpad.

The other lambda function can be used to perform a physical delete- delete from S3 glacier as well as from the database. Similar to soft delete, it should first verify with CMR and/or Cumulus that the granule has been deleted from those locations before deleting from ORCA. This will require further discussion with Cumulus team before performing the actual work.


### Deleting objects from AWS S3

To delete an object from an S3 bucket, the [delete_objects](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects)
can be used from the boto3 library. An example of the usage can be seen below.
Some notable items if this library is used includes the following.
- It can be used to delete up to 1000 objects from a bucket using a single API call.
- When performing this action on an MFA Delete enabled bucket that attempts to delete any versioned objects, an MFA token must be included orelse it will fail.
- If the object specified in the request is not found, Amazon S3 returns the result as deleted.
- Each DeleteObjects API incurs a little cost.

#### Example Using delete_objects

```python
import boto3

s3_client = boto3.client('s3')
bucket = "riz-orca"
response = s3_client.delete_objects(
    Bucket=bucket,
    Delete={
        'Objects': [
            {
                'Key': 'MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf',
            }
        ]
    }
)
print(response)

# Results
{
   "ResponseMetadata":{
      "RequestId":"KJCZAPM0RWMJNNC7",
      "HostId":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",
      "HTTPStatusCode":200,
      "HTTPHeaders":{
         "x-amz-id-2":"z2fRlgMxT10ApzcyDOLp3REn3PjM71OSgdH0oPpe4v2pHchmSTPCfEjBjTx00PyTL55wgmQ7gF4=",
         "x-amz-request-id":"KJCZAPM0RWMJNNC7",
         "date":"Tue, 08 Mar 2022 05:19:07 GMT",
         "content-type":"application/xml",
         "transfer-encoding":"chunked",
         "server":"AmazonS3",
         "connection":"close"
      },
      "RetryAttempts":0
   },
   "Deleted":[
      {
         "Key":"MOD09A1.006/MOD09A1.A2019025.h07v03.006.2019037205734.hdf"
      }
   ]
}
```
### Logging

Additional logging should be collected during the deletion process to keep records for safety and security purposes. Some logging to capture might include who deleted the data, when how many granules were deleted over a particular timespan, from which collections was it deleted, and what workflow was used to delete them.

Cloudwatch logs and cloudtrail can be used to collect logging information. In addition, S3 server access logging can be used at the bucket level which would provide detailed records for the requests that are made to a bucket. The log information can be useful in security and access audits. AWS will collect access log records, add the records in log files, and then upload log files to the target bucket as log objects. There is no extra charge for using the service except the cost for storing the log files in S3.

## Future directions

Few cards have been created to perform the ORCA delete functionality work based on initial research. This should be revisited during PI planning/team meetings to confirm the use cases/requirements before starting the work.
Some of the cards created to finish the task include:
- https://bugs.earthdata.nasa.gov/browse/ORCA-394- Create Lambda function for performing soft deletes from ORCA
- https://bugs.earthdata.nasa.gov/browse/ORCA-395- Create Lambda function for performing physical/hard deletes from ORCA
- https://bugs.earthdata.nasa.gov/browse/ORCA-396- Create API gateway resource for performing ORCA delete functionality
- https://bugs.earthdata.nasa.gov/browse/ORCA-397- Integrate ORCA delete API gateways with Launchpad and add users who can perform the deletion.
- https://bugs.earthdata.nasa.gov/browse/ORCA-398- Investigate logging for ORCA delete functionality.


##### References
- https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Data+Management+Use+Cases
- https://wiki.earthdata.nasa.gov/display/CUMULUS/ORCA+Prevention+Use+Cases
- https://wiki.earthdata.nasa.gov/display/CUMULUS/2022-03-02+ORCA+Meeting+notes
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_objects